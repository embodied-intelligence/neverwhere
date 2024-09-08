import numpy as np
import torch
from PIL import Image
from params_proto import ParamsProto, Proto
from time import sleep
from zaku import TaskQ

from lucidsim.traj_samplers import flow_gen


class WarpNode(ParamsProto, prefix="warper"):
    data_server = Proto(env="WEAVER_DATA_SERVER")
    queue_name = Proto(env="$ZAKU_USER:lucidsim:warping-queue-1")
    device = "cuda:0"

    def __post_init__(self):
        from ml_logger import ML_Logger

        print("subscribing to the worker queue.")
        self.logger = ML_Logger(root=self.data_server)
        self.logger.print("created warp node", color="green")

        self.queue = TaskQ(name=self.queue_name)

        print("Logger:", self.logger)

    def generate(self, *, env_name, seed, dataset_prefix, rollout_id, camera_id, width, height, baseline_interval):
        source_images = []
        with self.logger.Prefix(dataset_prefix):
            (traj,) = self.logger.load_pkl(f"{rollout_id}_trajectory.pkl")

            image_filenames = sorted(self.logger.glob(f"{rollout_id}_imagen/*.jpeg"))
            for image_filename in image_filenames:
                buff = self.logger.load_file(image_filename)
                img = np.array(Image.open(buff))
                img_t = torch.from_numpy(img).to(self.device)
                source_images.append(img_t)

        poses = list(zip(traj["cam_pos"], traj["cam_rot"]))

        if len(source_images) != len(poses):
            print(f"Number of images {len(source_images)} and poses {len(poses)} do not match. Skipping...")
            return

        gen = flow_gen.main(
            poses=poses,
            source_images=source_images,
            env_name=env_name,
            camera_name=camera_id,
            width=width,
            height=height,
            seed=seed,
            baseline_interval=baseline_interval,
            device=self.device,
        )

        with self.logger.Prefix(f"{dataset_prefix}"):
            fnames = []
            for step, flow_results in enumerate(gen):
                save_path = f"{rollout_id}_imagen-warped_{baseline_interval}/frame_{step:04d}.jpeg"
                self.logger.save_image(flow_results["warped"], save_path)
                fnames.append(save_path)

            # self.logger.make_video(fnames, f"{rollout_id}_imagen-warped_{baseline_interval}.mp4", fps=50)

        print("Saved the warping results to ", f"{dataset_prefix}/{rollout_id}_imagen-warped.mp4")

    def run(self, _deps=None, **deps):
        print("starting the worker...")
        while True:
            with self.queue.pop() as job_kwargs:
                if job_kwargs is None:
                    self.logger.print(".", end="", color="yellow")
                    sleep(3.0)
                    continue

                if job_kwargs.get("$kill", None):
                    exit()

                self.generate(**job_kwargs)


def entrypoint(**deps):
    worker = WarpNode(**deps)
    worker.run()


if __name__ == "__main__":
    from params_proto.hyper import Sweep
    # entrypoint()
    # exit()

    jobs = []
    for collection in [
        "chase_soccer_ball_red_brick_courtyard_prompts_v4",
        "chase_soccer_ball_blue_lab_carpet_prompts_v1",
        # "chase_soccer_ball_grassy_courtyard_prompts_v2",
        "chase_cones_red_brick_courtyard_prompts_v4",
        "chase_cones_lab_blue_carpet_prompts_v1",
        "chase_cones_grassy_courtyard_prompts_v2",
    ]:
        jobs += Sweep.read(f"../../../lucidsim_experiments/datasets/lucidsim_v1/{collection}/sweep/warp_5.jsonl")

    worker = WarpNode()

    # queue = TaskQ(name=worker.queue_name)
    # queue.clear_queue()
    # queue.add(job_kwargs)

    for job in jobs:
        worker.generate(**job)

    exit()

    dataset_prefix = "/lucidsim/lucidsim/corl/test-teacher-node/experiments/extension_stairs_wh_cones_gpt_prompts_v1/debug-18-35-06-366080"
    rollout_id = "debug-18-35-06-366080"
    env_name = "Extensions-cones-stairs_wh-lucidsim-v1"

    worker = WarpNode()
    job_kwargs = dict(
        env_name=env_name,
        dataset_prefix=dataset_prefix,
        rollout_id=rollout_id,
        # fov: 90
        camera_id="flow-cam",
        width=320,
        height=180,
        seed=1,
        baseline_interval=5,
    )

    worker.run()
