from params_proto.hyper import Sweep
from pathlib import Path

from neverwhere.traj_samplers.unroll import Unroll
from neverwhere_baselines.expert import RUN

if __name__ == "__main__":
    with Sweep(RUN, Unroll) as sweep:
        Unroll.render = True
        Unroll.log_metrics = True
        Unroll.num_steps = 300
        Unroll.vision_key = 'vision'
        Unroll.seed = 500
        Unroll.checkpoint = '/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt'

        with sweep.product:
            Unroll.env_name = [
                "Real-heightmap-chase-real_flat_01_stata_grass",
                "Real-heightmap-chase-real_flat_02_wh_evening",
                "Real-heightmap-chase-real_flat_03_stata_indoor"
            ]

    @sweep.each
    def tail(RUN, Unroll):
        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")
