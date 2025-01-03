from neverwhere import add_env
from neverwhere.tasks import parkour

# scenes available in "neverwhere_envs/scene_list.txt"
prefix = "nw-"
SPAWN_X_RAND = 0.1
SPAWN_Y_RAND = 0.1
SPAWN_YAW_RAND = 0.1

add_env(
    env_id=f"Neverwhere-heightmap-gaps_12in_226_blue_carpet_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_12in_226_blue_carpet_v2",
        xml_path=f"{prefix}gaps_12in_226_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-gaps_16in_226_blue_carpet_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_16in_226_blue_carpet_v2",
        xml_path=f"{prefix}gaps_16in_226_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-gaps_grassy_courtyard_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_grassy_courtyard_v2",
        xml_path=f"{prefix}gaps_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-gaps_stata_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-hurdle_226_blue_carpet_v3-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_226_blue_carpet_v3",
        xml_path=f"{prefix}hurdle_226_blue_carpet_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-hurdle_black_stone_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_black_stone_v1",
        xml_path=f"{prefix}hurdle_black_stone_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.8, # y limit: 1.2
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-hurdle_one_blue_carpet_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_one_blue_carpet_v2",
        xml_path=f"{prefix}hurdle_one_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.35, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-hurdle_stata_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_stata_v1",
        xml_path=f"{prefix}hurdle_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.35, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-hurdle_stata_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_stata_v2",
        xml_path=f"{prefix}hurdle_stata_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.5, # y limit: 0.7
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-hurdle_three_grassy_courtyard_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_three_grassy_courtyard_v2",
        xml_path=f"{prefix}hurdle_three_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.4, # y limit: 0.6
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-ramp_aligned_blue_carpet_v4-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_aligned_blue_carpet_v4",
        xml_path=f"{prefix}ramp_aligned_blue_carpet_v4.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-ramp_bricks_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_bricks_v2",
        xml_path=f"{prefix}ramp_bricks_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-ramp_grass_v3-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_grass_v3",
        xml_path=f"{prefix}ramp_grass_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-ramp_spread_blue_carpet_v5-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_spread_blue_carpet_v5",
        xml_path=f"{prefix}ramp_spread_blue_carpet_v5.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-building_31_stairs_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="building_31_stairs_v1",
        xml_path=f"{prefix}building_31_stairs_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.6, # y limit: 0.8
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-real_hurdle_three_grassy_ally_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_hurdle_three_grassy_ally_v2",
        xml_path=f"{prefix}real_hurdle_three_grassy_ally_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.4, # y limit: 0.6
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-real_stair_02_bcs_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_02_bcs_v1",
        xml_path=f"{prefix}real_stair_02_bcs_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.7, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-real_stair_04_bcs_dusk-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_04_bcs_dusk",
        xml_path=f"{prefix}real_stair_04_bcs_dusk.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.7, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-real_stair_08_mc_afternoon_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_08_mc_afternoon_v1",
        xml_path=f"{prefix}real_stair_08_mc_afternoon_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-stairs_4_stairs2up_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_4_stairs2up_v1",
        xml_path=f"{prefix}stairs_4_stairs2up_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-stairs_36_backstairs_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_36_backstairs_v2",
        xml_path=f"{prefix}stairs_36_backstairs_v2.xml",
        n_proprio=53,
        x_noise=0.10, # x limit: 0.2
        y_noise=0.6, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-stairs_48_v3-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_48_v3",
        xml_path=f"{prefix}stairs_48_v3.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-wood_ramp_aligned_bricks_v1-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_aligned_bricks_v1",
        xml_path=f"{prefix}wood_ramp_aligned_bricks_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-wood_ramp_aligned_grass_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_aligned_grass_v2",
        xml_path=f"{prefix}wood_ramp_aligned_grass_v2.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)

add_env(
    env_id=f"Neverwhere-heightmap-wood_ramp_offset_bricks_v2-cones",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_offset_bricks_v2",
        xml_path=f"{prefix}wood_ramp_offset_bricks_v2.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
    ),
)