from params_proto.hyper import Sweep
from pathlib import Path

from neverwhere.traj_samplers.unroll import Unroll
from neverwhere_baselines.expert import RUN

if __name__ == "__main__":
    with Sweep(RUN, Unroll) as sweep:
        Unroll.render = True
        Unroll.log_metrics = True
        Unroll.num_steps = 500
        Unroll.vision_key = None
        Unroll.delay = 0
        Unroll.checkpoint = "/lucid-sim/lucid-sim/baselines/launch_intermediate_ckpts_v3/go1/delay_4/300/checkpoints/model_last.pt"

        with sweep.product:
            Unroll.env_name = [
                "Real-heightmap-hurdle_226_blue_carpet_v3-cones",
                "Real-heightmap-hurdle_one_blue_carpet_v2-cones",
                "Real-heightmap-hurdle_one_dark_grassy_courtyard_v1-cones",
                "Real-heightmap-hurdle_one_light_grassy_courtyard_v3-cones",
                "Real-heightmap-hurdle_stata_one_v1-cones",
                "Real-heightmap-hurdle_stata_v2-cones",
                "Real-heightmap-hurdle_three_grassy_courtyard_v2-cones"
            ]

    @sweep.each
    def tail(RUN, Unroll):
        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")
