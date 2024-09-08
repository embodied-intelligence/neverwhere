import numpy as np
import os
from ml_logger import ML_Logger
from params_proto import ParamsProto


def get_metrics(task, ckpt, loader):
    exp_name = f"{task.capitalize()}-heightmap-v1/ckpt-{ckpt}"

    # print(loader)

    with loader.Prefix(exp_name):
        succ, delta_x = loader.read_metrics(
            "frac_goals_reached",
            "x_displacement",
            path="episode_metrics.pkl",
            num_bins=1,
        )

    return succ.mean()[0], delta_x.mean()[0]


class UniformCheckpointSampler(ParamsProto):
    experiment_prefix = "/lucid-sim/lucid-sim/baselines/launch_intermediate_ckpts_v2/go1/200"
    metrics_prefix = "/lucidsim/lucidsim/corl_experiments/sweeps/parkour/subpar_experts/subpar_experts"

    def __post_init__(self):
        # grab all of the success rates
        loader = ML_Logger(prefix=self.metrics_prefix)
        with loader.Prefix(self.experiment_prefix):
            checkpoint_paths = loader.glob("checkpoints/*.pt")
            checkpoint_paths = [path for path in checkpoint_paths if "last" not in path]

            checkpoint_steps = {path: int(path.split("_")[-1].split(".")[0]) for path in checkpoint_paths}

            self.checkpoint_paths = sorted(checkpoint_paths, key=lambda x: checkpoint_steps[x])
            self.checkpoint_steps = [int(path.split("_")[-1].split(".")[0]) for path in self.checkpoint_paths]

    def sample(self):
        idx = np.random.randint(len(self.checkpoint_steps))
        ckpt_path = os.path.join(self.experiment_prefix, self.checkpoint_paths[idx])

        return ckpt_path


if __name__ == "__main__":
    sampler = UniformCheckpointSampler()
    for _ in range(10):
        print(sampler.sample())
