"""
Setup a simple funciton that takes the config and pumps the
data in to a queue.

Usage: We will call this from a different launch script that
scales this up on the cluster

1. setup the sweep here (use paramsproto, think of the right way)
2. add the
"""

from collections import defaultdict

import numpy as np
import uuid
from copy import copy
from params_proto import ParamsProto, Proto
from time import sleep
from zaku import TaskQ

from lucidsim.traj_samplers import unroll_stream
from lucidsim.utils.utils import pick


class TeacherNode(ParamsProto, prefix="teacher"):
    data_server = Proto(env="WEAVER_DATA_SERVER")

    queue_name = Proto(env="$ZAKU_USER:lucidsim:teacher-queue-1")
    weaver_queue_name = Proto(env="$ZAKU_USER:lucidsim:weaver-queue-1")
    weaver_output_queue_name = Proto(env="$ZAKU_USER:lucidsim:weaver-queue-out")

    def __post_init__(self):
        from ml_logger import ML_Logger

        print("subscribing to the worker queue.")
        self.queue = TaskQ(name=self.queue_name)
        self.weaver_queue = TaskQ(name=self.weaver_queue_name)
        self.weaver_output_queue = TaskQ(name=self.weaver_output_queue_name)
        self.logger = ML_Logger(root=self.data_server)
        self.logger.print("created teacher node", color="green")

        print("Logger:", self.logger)

    def run(self, _deps=None, **deps):
        print("starting the worker...")
        while True:
            with self.queue.pop() as job_kwargs:
                if job_kwargs is None:
                    self.logger.print(".", end="", color="yellow")
                    sleep(3.0)  # no need to query frequently when queue is empty.
                    continue

                # untested
                if job_kwargs.get("$kill", None):
                    exit()

                print("generating", end=",")

                seed = job_kwargs.get("seed", None)
                seed_generator = np.random.RandomState(seed)

                logger_prefix = job_kwargs.pop("unroll.logger_prefix", ".")

                streaming_mode = job_kwargs.pop("streaming_mode", False)

                if self.data_server.startswith("/"):
                    # remove any leading slashes in the provided prefix
                    logger_prefix = logger_prefix.lstrip("/")

                gen = unroll_stream.main(job_kwargs)

                traj = defaultdict(list)

                rollout_id = str(uuid.uuid4())
                rollout_id = job_kwargs.get("rollout_id", rollout_id)

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

                        # for flow
                        traj["cam_pos"].append(frame["cam_pos"])
                        traj["cam_rot"].append(frame["cam_rot"])

                        # Below is not needed: label during training
                        # traj["teacher_act"].append(frame["teacher_act"])

                        worker_kwargs = dict(
                            to_logger=f"{rollout_id}_imagen/frame_{step:05}.png",
                            logger_prefix=logger_prefix,
                            seed=seed_generator.randint(0, 1_000_000_000),
                            **pick(frame, "midas_depth", "foreground_mask", "background_mask", "cone_mask"),
                            **_k,
                        )

                        if streaming_mode:
                            generated_kwargs = self.weaver_queue.rpc(**worker_kwargs, _timeout=300)
                            # wait for the weaver to return the next frame
                            generated = generated_kwargs.get("generated")
                        else:
                            self.weaver_queue.add(worker_kwargs)
                            generated = None

                        with self.logger.Prefix(logger_prefix):
                            for k in pick(frame, "render_rgb", "midas_depth", "render_depth"):
                                img = frame[k]
                                save_path = f"{rollout_id}_ego_views/{k}/frame_{step:05}.jpeg"
                                self.logger.save_image(img, save_path)

                            for k in pick(frame, "foreground_mask", "background_mask", "cone_mask"):
                                img = frame[k]
                                save_path = f"{rollout_id}_ego_views/{k}/frame_{step:05}.png"
                                self.logger.save_image(img, save_path)

                        # add streaming logic
                        print("sent", step)
                        frame = gen.send(generated)
                        step += 1

                    except StopIteration:
                        print("wtf", step)
                        break

                with self.logger.Prefix(logger_prefix):
                    traj_save_path = f"{rollout_id}_trajectory.pkl"
                    self.logger.save_pkl(traj, traj_save_path)


def entrypoint(**deps):
    worker = TeacherNode(**deps)
    worker.run()


class TWO_PROMPTS:
    control_strength = 0.8
    foreground_prompt = "orange cone"
    background_prompt = "long description"

    # The prompt list should be the same length as the rollout right now
    prompt_list = [
        {
            "control_strength": 0.9,
            "title": "Overexposed Courtyard on a Bright Day",
            "description": "A modernist building barely visible due to overexposure. Few trees with green leaves.",
            "foreground_prompt": "An orange colored cone on the flat ground.",
            "background_prompt": "A modernist building barely visible due to overexposure. Few trees with green leaves.",
            "negative_prompt": "dogs, labrador, golden retrievers",
            "metadata": {"lucidsim_task": "chase-cones", "scene": "Red-brick courtyard"},
        },
        {
            "control_strength": 0.9,
            "title": "Autumn Feel in Courtyard with Falling Leaves",
            "description": "The courtyard with scattered leaves from green-leaved trees and an imposing brick building.",
            "foreground_prompt": "An orange colored cone on the flat ground.",
            "background_prompt": "The courtyard with scattered leaves from green-leaved trees and an imposing brick building.",
            "negative_prompt": "dogs, labrador, golden retrievers",
            "metadata": {"lucidsim_task": "chase-cones", "scene": "Red-brick courtyard"},
        },
    ]


if __name__ == "__main__":
    entrypoint()

    exit()
    from params_proto.hyper import Sweep
    from ml_logger import logger

    print(logger.get_dash_url())

    collection_name = "extension_stairs_wh_cones_gpt_prompts_v2_filtered"
    prompt_list = Sweep.read(f"../../../lucidsim_experiments/datasets/lucidsim_v1/_collections/{collection_name}.jsonl")

    job = {
        "prompt_list": prompt_list,
        "unroll.logger_prefix": f"/{logger.prefix}",
        "unroll.render": True,
        "unroll.env_name": "Extensions-cones-stairs_wh-lucidsim_sampling-v1",
        "unroll.stop_after_termination": True,
        "unroll.model_cls": "behavior_cloning.go1_model.transformers.transformer_policy:TransformerPolicy",
        "unroll.checkpoint": "/alanyu/scratch/2024/05-20/010810/checkpoints/net_last.pt",
        "streaming_mode": True,
        "control_strength": 1.0,
        "render_kwargs": {
            "workflow_cls": "weaver.workflows.three_mask_workflow:ImagenCone",
            "downscale": 4,
        },
    }

    print("logger prefix", logger.prefix)
    debug_teacher_queue_name = f"{TaskQ.ZAKU_USER}:lucidsim:debug-teacher-queue-1"
    debug_weaver_queue_name = f"{TaskQ.ZAKU_USER}:lucidsim:debug-weaver-queue-1"

    debug_teacher_queue = TaskQ(name=debug_teacher_queue_name)
    debug_teacher_queue.clear_queue()

    debug_teacher_queue.add(job)

    entrypoint(
        queue_name=debug_teacher_queue_name,
        weaver_queue_name=debug_weaver_queue_name,
    )
    exit()
