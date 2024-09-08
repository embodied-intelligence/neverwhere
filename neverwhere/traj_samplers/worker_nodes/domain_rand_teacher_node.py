import uuid
from collections import defaultdict
from time import sleep

from params_proto import ParamsProto, Proto
from zaku import TaskQ

from lucidsim.traj_samplers import unroll_stream
from lucidsim.utils.utils import pick


class DRTeacherNode(ParamsProto, prefix="teacher"):
    data_server = Proto(env="WEAVER_DATA_SERVER")
    queue_name = Proto(env="$ZAKU_USER:lucidsim:dr-teacher-queue-1")

    save_small = True
    downscale = 4

    check_existing = True

    def __post_init__(self):
        from ml_logger import ML_Logger

        print("subscribing to the worker queue.")
        self.queue = TaskQ(name=self.queue_name)

        self.logger = ML_Logger(root=self.data_server)
        self.logger.print("created domain rand teacher node", color="green")

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

                logger_prefix = job_kwargs.pop("unroll.logger_prefix", ".")

                gather_queue_name = job_kwargs.pop("_gather_id", None)
                gather_token = job_kwargs.pop("_gather_token", None)

                if self.data_server.startswith("/"):
                    # remove any leading slashes in the provided prefix
                    logger_prefix = logger_prefix.lstrip("/")

                rollout_id = str(uuid.uuid4())
                rollout_id = job_kwargs.get("rollout_id", rollout_id)

                if self.check_existing:
                    with self.logger.Prefix(logger_prefix):
                        traj_save_path = f"{rollout_id}_trajectory.pkl"
                        glob_list = self.logger.glob("*")
                        if glob_list is not None and traj_save_path in glob_list:
                            print(f"trajectory {traj_save_path} already exists, skipping")
                            if gather_queue_name is not None:
                                gather_queue = TaskQ(name=gather_queue_name)
                                gather_queue.add({"_gather_token": gather_token})
                            continue

                gen = unroll_stream.main(job_kwargs)

                traj = defaultdict(list)

                for step, frame in enumerate(gen):
                    traj["obs"].append(frame["obs"])

                    save_kwargs = pick(frame, "render_rgb")

                    with self.logger.Prefix(logger_prefix):
                        for k, img in save_kwargs.items():
                            to_file = f"{rollout_id}_ego_views/{k}/frame_{step:05}.jpeg"
                            if self.save_small:
                                fname = to_file.split(".")[0]

                                # crop and resize
                                img = img.resize((img.size[0] // self.downscale, img.size[1] // self.downscale))

                                saved_path = self.logger.save_image(img, f"{fname}_{self.downscale}x.jpeg")
                                print(f"saved to {saved_path}")

                            else:
                                saved_path = self.logger.save_image(img, to_file)
                                print(f"saved to {saved_path}")

                # save traj, once at the end of the rollout
                with self.logger.Prefix(logger_prefix):
                    traj_save_path = f"{rollout_id}_trajectory.pkl"
                    self.logger.save_pkl(traj, traj_save_path)

                if gather_queue_name is not None:
                    gather_queue = TaskQ(name=gather_queue_name)
                    gather_queue.add({"_gather_token": gather_token})


def entrypoint(**deps):
    print("in entrypoint")
    worker = DRTeacherNode(**deps)
    worker.run()


if __name__ == "__main__":
    entrypoint()
    exit()
    sweep = Sweep.read(
        "../../../lucidsim_experiments/datasets/domain_randomization_7_v1/extensions_cones_stairs_wh_v1/dagger_2/data_gen.jsonl"
    )
    job = sweep[0]

    debug_queue_name = DRTeacherNode.queue_name + ":debug"
    queue = TaskQ(name=debug_queue_name)
    queue.add(job)
    entrypoint(queue_name=debug_queue_name)
