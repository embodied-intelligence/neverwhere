from collections import defaultdict
from time import sleep

import numpy as np
import uuid
from copy import copy
from params_proto import ParamsProto, Proto
from zaku import TaskQ

from lucidsim.traj_samplers import unroll_flow_stream
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

    assert not queue_name.value.startswith(":"), "need to have ZAKU_USER set, otherwise this will err silently"
    assert not weaver_queue_name.value.startswith(":"), "need to have ZAKU_USER set, otherwise this will err silently"

    save_conditioning = False

    check_existing = True

    def __post_init__(self):
        from ml_logger import ML_Logger

        print("subscribing to the worker queue:", self.queue_name)
        self.queue = TaskQ(name=self.queue_name)
        self.weaver_queue = TaskQ(name=self.weaver_queue_name)

        self.logger = ML_Logger(root=self.data_server)
        print("created flow teacher node")

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

                gen = unroll_flow_stream.main(job_kwargs)

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
                    "cone_strength",
                    "background_prompt",
                    "foreground_prompt",
                    "render_kwargs",
                )

                # prime generator
                step = 0
                frame = next(gen)
                prompt_offset = seed_generator.randint(0, num_prompts) if num_prompts > 0 else 0

                while True:
                    try:
                        if prompt_list:
                            _k = copy(kwargs)
                            # weaver_cfg = prompt_list[(step + prompt_offset) % num_prompts]
                            weaver_cfg = seed_generator.choice(prompt_list)
                            _k.update(weaver_cfg)
                        else:
                            _k = kwargs

                        traj["obs"].append(frame["obs"])

                        # for offline flow, if needed later
                        traj["cam_pos"].append(frame["cam_pos"])
                        traj["cam_rot"].append(frame["cam_rot"])

                        # check the contract
                        generated_image = frame.get("generated_image", None)
                        offline_generation = frame.get("offline_generation", False)

                        if offline_generation:
                            assert generated_image is None, "offline generation is True, but you expected a warped frame"

                        to_logger = f"{rollout_id}_imagen-warped_{baseline_interval}/frame_{step:05}.jpeg"

                        if generated_image is None:
                            # make rpc call
                            worker_kwargs = dict(
                                seed=seed_generator.randint(0, 1_000_000_000),
                                **pick(frame, "midas_depth", "foreground_mask", "background_mask", "cone_mask"),
                                **_k,
                            )
                            # print("requested generation with keys ", worker_kwargs.keys())

                            if offline_generation:
                                self.weaver_queue.add(dict(**worker_kwargs, logger_prefix=logger_prefix, to_logger=to_logger))
                                generated_image = None
                            else:
                                generated_kwargs = self.weaver_queue.rpc(**worker_kwargs, _timeout=300)
                                generated_image = generated_kwargs.get("generated")

                        with self.logger.Prefix(logger_prefix):
                            if not offline_generation:
                                saved_path = self.logger.save_image(generated_image, to_logger)

                            if self.save_conditioning:
                                for k in pick(frame, "render_rgb", "midas_depth", "render"):
                                    img = frame[k]
                                    save_path = f"{rollout_id}_ego_views/{k}/frame_{step:05}.jpeg"
                                    self.logger.save_image(img, save_path)

                                for k in pick(frame, "foreground_mask", "background_mask", "cone_mask"):
                                    img = frame[k]
                                    save_path = f"{rollout_id}_ego_views/{k}/frame_{step:05}.png"
                                    self.logger.save_image(img, save_path)

                        # print("sent", step)
                        frame = gen.send(generated_image)
                        step += 1

                    except StopIteration:
                        print("Ended on the step number", step)
                        break

                with self.logger.Prefix(logger_prefix):
                    traj_save_path = f"{rollout_id}_trajectory.pkl"
                    self.logger.save_pkl(traj, traj_save_path)

                print("finished", rollout_id)

                if gather_queue_name is not None:
                    gather_queue = TaskQ(name=gather_queue_name)
                    gather_queue.add({"_gather_token": gather_token})
                    print("sent gather token back to", gather_queue_name)


def entrypoint(**deps):
    worker = FlowTeacherNode(**deps)
    worker.run()


if __name__ == "__main__":
    entrypoint(queue_name="alanyu:lucidsim:flow-teacher-queue-3", weaver_queue_name="alanyu:lucidsim:weaver-queue-1")
    exit()

    from ml_logger import logger
    from params_proto.hyper import Sweep

    print(logger.get_dash_url())

    collection_name = "extensions_hurdle_ground_prompt_v1"
    prompt_list = Sweep.read(f"../../../lucidsim_experiments/datasets/lucidsim_v1/_collections/{collection_name}.jsonl")

    # job = {
    #     "prompt_list": prompt_list,
    #     "unroll.logger_prefix": f"/{logger.prefix}",
    #     "unroll.render": True,
    #     "unroll.baseline_interval": 7,
    #     "unroll.vision_key": "imagen",
    #     "unroll.env_name": "Extensions-hurdle_many-lucidsim_sampling-v1",
    #     "unroll.stop_after_termination": True,
    #     "unroll.width": 320,
    #     "unroll.height": 180,
    #     "unroll.seed": 5000,
    #     "unroll.model_entrypoint": "behavior_cloning.go1_model.transformers.transformer_policy:get_rgb_transformer_policy_batchnorm",
    #     "unroll.checkpoint": "/lucidsim/lucidsim/corl_experiments/datasets/lucidsim_v1/extensions_hurdle_many_combined_prompts_v1/sweep/sweep/Extensions-hurdle_many-lucidsim-v1/train/dagger_3/checkpoints/net_60.pt",
    #     "control_strength": 0.8,
    #     "render_kwargs": {
    #         "workflow_cls": "weaver.workflows.three_mask_workflow:ImagenCone",
    #         "downscale": 4,
    #         "crop_size": (1280, 720),
    #     },
    # }

    # job = {
    #     "prompt_list": prompt_list,
    #     "unroll.logger_prefix": f"/{logger.prefix}",
    #     "unroll.render": True,
    #     "unroll.baseline_interval": 7,
    #     "unroll.vision_key": None,
    #     "unroll.env_name": "Extensions-hurdle_many-lucidsim_realsense-v1",
    #     "unroll.stop_after_termination": True,
    #     "unroll.width": 320,
    #     "unroll.height": 180,
    #     "unroll.seed": 5000,
    #     "unroll.model_entrypoint": "cxx.modules.parkour_actor:get_parkour_teacher_policy",
    #     "unroll.checkpoint": "/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt",
    #     "unroll.camera_name": "realsense-rgb-render",
    #     "control_strength": 0.8,
    #     "cone_strength": 0.8,
    #     "render_kwargs": {
    #         "workflow_cls": "weaver.workflows.three_mask_workflow:ImagenCone",
    #         "downscale": 4,
    #         "crop_size": (1280, 720),
    #     },
    # }

    job = Sweep.read("../../../lucidsim_experiments/datasets/lucidsim_v1/chase_cones_combined_v1/sweep/lucidsim_datagen.jsonl")[0]
    job["unroll.logger_prefix"] = f"/{logger.prefix}"
    job["unroll.width"] = 320
    job["unroll.height"] = 180

    print("logger prefix", logger.prefix)
    debug_teacher_queue_name = f"{TaskQ.ZAKU_USER}:lucidsim:debug-flow-teacher-queue-1"
    debug_weaver_queue_name = f"{TaskQ.ZAKU_USER}:lucidsim:debug-weaver-queue-1"

    debug_teacher_queue = TaskQ(name=debug_teacher_queue_name)
    debug_teacher_queue.clear_queue()

    debug_teacher_queue.add(job)

    entrypoint(
        queue_name=debug_teacher_queue_name,
        weaver_queue_name=debug_weaver_queue_name,
        save_conditioning=True,
    )
    exit()
