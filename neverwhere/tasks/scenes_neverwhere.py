from neverwhere import add_env
from neverwhere.tasks import chase
from neverwhere.tasks import parkour
from neverwhere.tasks.base.ball import Ball

available_scenes_list = open("neverwhere_envs/scene_list.txt").read().splitlines()

for scene in available_scenes_list:
    add_env(
        env_id=f"Neverwhere-heightmap-{scene}-cones",
        entrypoint=parkour.entrypoint,
        kwargs=dict(
            check_contact_termination=True,
            mode="heightmap_splat",
            dataset_name=scene,
            xml_path=f"neverwhere_{scene}.xml",
            n_proprio=53,
            x_noise=0,
            y_noise=0.1,
            spawn_x_rand=0.1,
            spawn_y_rand=0.1,
            spawn_yaw_rand=0.1,
            splat_render_keys=["rgb"],
            use_cones=True,
        ),
    )