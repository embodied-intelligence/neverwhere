from lucidsim.traj_samplers.worker_nodes.teacher_node import TeacherNode

worker = TeacherNode()
worker.run(
    {
        "env_name": "Gaps-heightmap-v1",
        "checkpoint": "/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt",
        "vision_key": "heightmap",
        "num_steps": "",
        "delay": 0,
        "render": False,
        "seed": 100,
    }
)

{
    "unroll.checkpoint": "/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt",
    "unroll.render": False,
    "unroll.log_metrics": True,
    "unroll.delay": 0,
    "unroll.vision_key": None,
    "unroll.env_name": "Gaps-heightmap-v1",
    "unroll.seed": 0,
    "RUN.job_counter": 1,
    "RUN.prefix": "lucidsim/lucidsim/corl_experiments/sweeps/parkour/expert/expert/Gaps-heightmap-v1",
    "RUN.job_name": "Gaps-heightmap-v1",
}
