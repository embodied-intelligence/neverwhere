from collections import defaultdict

import uuid
from params_proto import ParamsProto, Proto
from time import sleep
from zaku import TaskQ

from lucidsim.traj_samplers import unroll_stream
from lucidsim.utils.utils import pick


class TeacherNode(ParamsProto, prefix="teacher"):
    data_server = Proto(env="WEAVER_DATA_SERVER")

    queue_name = "alan:lucidsim:splat-teacher-queue-1"

    def __post_init__(self):
        from ml_logger import ML_Logger

        print("subscribing to the worker queue.")
        self.queue = TaskQ(name=self.queue_name)

        self.logger = ML_Logger(root=self.data_server)
        self.logger.print("created splat teacher node", color="green")

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

                logger_prefix = job_kwargs.pop("unroll.logger_prefix", ".")

                if self.logger_root.startswith("/"):
                    # remove any leading slashes in the provided prefix
                    logger_prefix = logger_prefix.lstrip("/")

                gen = unroll_stream.main(job_kwargs)

                traj = defaultdict(list)
                rollout_id = str(uuid.uuid4())

                for step, frame in enumerate(gen):
                    traj["obs"].append(frame["obs"])

                    save_kwargs = pick(frame, "splat_rgb")

                    with self.logger.Prefix(logger_prefix):
                        for k, img in save_kwargs.items():
                            save_path = f"{rollout_id}_ego_views/{k}/frame_{step:05}.jpeg"
                            logger_saved_path = self.logger.save_image(img, save_path)
                            print(f"saved to {logger_saved_path}")

                # save traj, once at the end of the rollout
                with self.logger.Prefix(logger_prefix):
                    traj_save_path = f"{rollout_id}_trajectory.pkl"
                    self.logger.save_pkl(traj, traj_save_path)


def entrypoint(**deps):
    worker = TeacherNode(**deps)
    worker.run()


if __name__ == "__main__":
    entrypoint()
