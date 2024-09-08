import gc
import random
from time import sleep

from params_proto import ParamsProto
from params_proto import Proto

from lucidsim.traj_samplers import unroll


class EvalNode(ParamsProto, prefix="eval"):
    """Worker for evaluating an agent"""

    queue_name: str = Proto(env="$ZAKU_USER:lucidsim:eval-worker-queue-1")

    def __post_init__(self, worker_kwargs=None):
        from ml_logger import logger
        from zaku import TaskQ

        print("subscribing to the worker queue.")
        self.queue = TaskQ(name=self.queue_name)

        logger.print("created workflow", color="green")

    def run(self):
        from ml_logger import logger

        print("starting the worker...")
        while True:
            with self.queue.pop() as job_kwargs:
                if job_kwargs is None:
                    logger.print(".", end="", color="yellow")
                    sleep(3.0)  # no need to query frequently when queue is empty.
                    continue

                # untested
                if job_kwargs.get("$kill", None):
                    exit()

                print(*job_kwargs.keys())
                logger.print("generating", color="green")

                for i in range(3):
                    try:
                        unroll.main(job_kwargs)
                        break
                    except FileNotFoundError as e:
                        print("Lock issue encountered when rendering gsplat, retrying...")
                        print(f"The error was: {e}")
                        sleep_time = random.random() * 5
                        sleep(sleep_time)
                else:
                    print("Failed to render gsplat after 3 retries. Putting job back")
                    self.queue.add(job_kwargs)

                gc.collect()


def entrypoint(**deps):
    worker = EvalNode(**deps)
    worker.run()


if __name__ == "__main__":
    # from params_proto.hyper import Sweep
    #
    # sweep = Sweep.read()

    # q = TaskQ(name="alanyu:lucidsim:eval-worker-queue-1")
    # q.clear_queue()

    entrypoint()
