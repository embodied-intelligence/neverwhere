from neverwhere.traj_samplers import unroll

unroll.main(
    env_name="Real-heightmap-hurdle_one_dark_grassy_courtyard_v1-cones",
    checkpoint="/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt",
    vision_key=None,
    render=True,
    num_steps=500,
    delay=0,
)
