from collections import defaultdict
from time import sleep

import numpy as np
import uuid
from PIL import Image
from copy import copy
from pandas import DataFrame
from params_proto import ParamsProto, Proto
from zaku import TaskQ

from lucidsim.traj_samplers import unroll_flow_viz
from lucidsim.utils.utils import pick


class FlowTeacherNode(ParamsProto, prefix="teacher"):
    """
    Similar to teacher node
    The environment yields at each step, but:

    - if it yields a warped frame, then this should replace the rendering call to weaver
    - if it yields conditioning images, then this teacher node should call weaver and send the generated image, so it can be used for warping future steps

    the warping interval should be determined by the job kwargs.
    """

    data_server = Proto(env="WEAVER_DATA_SERVER")

    queue_name = Proto(env="$ZAKU_USER:lucidsim:flow-teacher-queue-1")
    weaver_queue_name = Proto(env="$ZAKU_USER:lucidsim:weaver-queue-1")

    save_conditioning = False

    check_existing = True

    def __post_init__(self):
        from ml_logger import ML_Logger

        print("subscribing to the worker queue:", self.queue_name)
        self.queue = TaskQ(name=self.queue_name)
        self.weaver_queue = TaskQ(name=self.weaver_queue_name)

        self.logger = ML_Logger(root=self.data_server)
        print("created teacher node")

        print("Logger:", self.logger)

    def run(self, _deps=None, **deps):
        print("starting the worker...")
        while True:
            with self.queue.pop() as job_kwargs:
                if job_kwargs is None:
                    print(".", end="")
                    sleep(3.0)  # no need to query frequently when queue is empty.
                    continue

                # untested
                if job_kwargs.get("$kill", None):
                    exit()

                print("generating", end=",")

                seed = job_kwargs.get("seed", None)
                seed_generator = np.random.RandomState(seed)

                logger_prefix = job_kwargs.pop("unroll.logger_prefix", ".")

                rollout_id = str(uuid.uuid4())
                rollout_id = job_kwargs.get("rollout_id", rollout_id)

                gather_queue_name = job_kwargs.pop("_gather_id", None)
                gather_token = job_kwargs.pop("_gather_token", None)

                if self.check_existing:
                    with self.logger.Prefix(logger_prefix):
                        traj_save_path = f"{rollout_id}_trajectory.pkl"
                        glob_list = self.logger.glob("*")
                        if glob_list and traj_save_path in glob_list:
                            print(f"trajectory {traj_save_path} already exists, skipping")
                            if gather_queue_name is not None:
                                gather_queue = TaskQ(name=gather_queue_name)
                                gather_queue.add({"_gather_token": gather_token})
                            continue

                if self.data_server.startswith("/"):
                    # remove any leading slashes in the provided prefix for local logging
                    logger_prefix = logger_prefix.lstrip("/")

                gen = unroll_flow_viz.main(job_kwargs)

                traj = defaultdict(list)

                baseline_interval = job_kwargs.get("unroll.baseline_interval")

                # dump job kwargs
                job_kwargs_save_path = f"{rollout_id}_cfg.json"

                with self.logger.Prefix(logger_prefix):
                    self.logger.save_json(job_kwargs, job_kwargs_save_path)

                prompt_list = job_kwargs.get("prompt_list", [])
                num_prompts = len(prompt_list)

                kwargs = pick(
                    job_kwargs,
                    "control_strength",
                    "background_prompt",
                    "foreground_prompt",
                    "render_kwargs",
                )

                d = []

                # prime generator
                step = 0
                frame = next(gen)

                while True:
                    try:
                        if prompt_list:
                            _k = copy(kwargs)
                            weaver_cfg = prompt_list[step % num_prompts]
                            _k.update(weaver_cfg)
                        else:
                            _k = kwargs

                        traj["obs"].append(frame["obs"])

                        # for offline flow, if needed later
                        traj["cam_pos"].append(frame["cam_pos"])
                        traj["cam_rot"].append(frame["cam_rot"])

                        d.append(pick(frame, "pos", "quat", "joints"))

                        # check the contract
                        generated_image = frame.get("generated_image", None)
                        if generated_image is None:
                            # make rpc call
                            worker_kwargs = dict(
                                seed=seed_generator.randint(0, 1_000_000_000),
                                **pick(frame, "midas_depth", "foreground_mask", "background_mask", "cone_mask"),
                                **_k,
                            )
                            print("requested generation with keys ", worker_kwargs.keys())
                            generated_kwargs = self.weaver_queue.rpc(**worker_kwargs, _timeout=300)
                            generated_image = generated_kwargs.get("generated")

                        with self.logger.Prefix(logger_prefix):
                            to_logger = f"imagen/frame_{step:05}.png"
                            saved_path = self.logger.save_image(generated_image, to_logger)

                            if self.save_conditioning:
                                data = pick(
                                    frame,
                                    "foreground_mask",
                                    "background_mask",
                                    "cone_mask",
                                    "flow_image",
                                    "render_rgb",
                                    "midas_depth",
                                    "render",
                                    "ego_render",
                                )
                                for k in data:
                                    img = data[k]
                                    save_path = f"{k}/frame_{step:05}.png"
                                    self.logger.save_image(img, save_path)

                                total_width = 1280
                                single_width = 1280 // 5
                                top_images = [
                                    data["foreground_mask"],
                                    data["background_mask"],
                                    data["cone_mask"],
                                    Image.fromarray(data["flow_image"]),
                                    data["midas_depth"],
                                ]

                                main_image = data["render"].copy()

                                resized_top_images = [
                                    img.resize((single_width, int(img.height * (single_width / 1280)))) for img in top_images
                                ]

                                # Paste each top image next to each other at the top of the composite image
                                for i, img in enumerate(resized_top_images):
                                    main_image.paste(img, (i * single_width, 0), 0)

                                self.logger.save_image(main_image, f"composite/frame_{step:05}.png")

                        frame = gen.send(generated_image)
                        step += 1

                    except StopIteration:
                        print("Ended on the step number", step)
                        break

                with self.logger.Prefix(logger_prefix):
                    d = DataFrame(d)
                    self.logger.save_pkl(d, "trajectory.pkl")

                if gather_queue_name is not None:
                    gather_queue = TaskQ(name=gather_queue_name)
                    gather_queue.add({"_gather_token": gather_token})


def entrypoint(**deps):
    worker = FlowTeacherNode(**deps)
    worker.run()


if __name__ == "__main__":
    from params_proto.hyper import Sweep
    from ml_logger import logger

    # job = Sweep.read(
    #     "../../../lucidsim_experiments/datasets/lucidsim_v1/extensions_hurdle_cone_combined_prompts_v1-alan-flow_7/sweep/lucidsim_datagen.jsonl"
    # )[0]

    # job = Sweep.read("../../../lucidsim_experiments/datasets/lucidsim_v1/chase_cones_combined_v1/sweep/lucidsim_datagen.jsonl")[0]

    job = Sweep.read("../../../lucidsim_experiments/datasets/lucidsim_v1/chase_soccer_combined_v1/sweep/lucidsim_datagen.jsonl")[0]

    # job = Sweep.read(
    #     "../../../lucidsim_experiments/datasets/lucidsim_v1/extensions_cones_stairs_wh-bcs_prompts_v7_v1/sweep/lucidsim_datagen.jsonl"
    # )[0]

    # job["unroll.env_name"] = "Extensions-cones-stairs_wh-lucidsim-v1"
    job["unroll.vision_key"] = None
    job["unroll.logger_prefix"] = f"/{logger.prefix}"
    job["control_strength"] = 0.8
    job["render_kwargs"]["downscale"] = 1
    job["unroll.width"] = 1280
    job["unroll.height"] = 768
    # job["unroll.checkpoint"] = (
    #     "/lucidsim/lucidsim/corl_experiments/datasets/lucidsim_v1/extensions_cones_stairs_wh-bcs_prompts_v7_v1/sweep/sweep/Extensions-cones-stairs_wh-lucidsim-v1/train/dagger_3/checkpoints/net_60.pt"
    # )
    # job["unroll.model_entrypoint"] = "behavior_cloning.go1_model.transformers.transformer_policy:get_rgb_transformer_policy_batchnorm"

    queue_name = "alanyu:lucidsim:debug-flow-teacher-queue-1"
    q = TaskQ(name=queue_name)
    # q.clear_queue()
    q.add(job)

    weaver_queue_name = "alanyu:lucidsim:debug-weaver-queue-1"

    entrypoint(
        queue_name=queue_name,
        weaver_queue_name=weaver_queue_name,
        save_conditioning=True,
    )
