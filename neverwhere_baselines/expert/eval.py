import gc
import random
from time import sleep
from tqdm import tqdm

from params_proto import ParamsProto
from params_proto import Proto
from params_proto.hyper import Sweep

from lucidsim.traj_samplers import unroll

if __name__ == "__main__":
    sweep = Sweep.read("neverwhere_baselines/expert/chase_v2/sweep.jsonl")

    print("Total number of jobs:", len(sweep))
    for job_kwargs in tqdm(sweep):
        try:
            unroll.main(job_kwargs)
        except FileNotFoundError as e:
            print("Lock issue encountered when rendering gsplat, retrying...")
            print(f"The error was: {e}")
            sleep_time = random.random() * 5
            sleep(sleep_time)
