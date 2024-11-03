from neverwhere import add_env
from neverwhere.tasks import chase
from neverwhere.tasks import parkour
from neverwhere.tasks.base.ball import Ball

add_env(
    env_id="Neverwhere-heightmap-curb_gas_tank_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=False,
        mode="heightmap_splat",
        dataset_name="curb_gas_tank_v1",
        xml_path="neverwhere_curb_gas_tank_v1.xml",
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

add_env(
    env_id="Neverwhere-heightmap-gaps_12in_226_blue_carpet_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=False,
        mode="heightmap_splat",
        dataset_name="gaps_12in_226_blue_carpet_v2",
        xml_path="neverwhere_gaps_12in_226_blue_carpet_v2.xml",
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

add_env(
    env_id="Neverwhere-heightmap-gaps_fire_outlet_v3-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=False,
        mode="heightmap_splat",
        dataset_name="gaps_fire_outlet_v3",
        xml_path="neverwhere_gaps_fire_outlet_v3.xml",
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