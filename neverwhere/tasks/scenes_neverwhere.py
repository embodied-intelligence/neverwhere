from neverwhere import add_env
from neverwhere.tasks.parkour import entrypoint
from ml_logger.job import instr

# scenes available in "neverwhere_envs/scene_list.txt"
prefix = "nw"
SPAWN_X_RAND = 0.1
SPAWN_Y_RAND = 0.1
SPAWN_YAW_RAND = 0.1

entrypoint = instr(entrypoint, stack_size=7) # set stack size to 7 as default


add_env(
    env_id="nw-go1-gaps_many-vision_depth_act-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        xml_path="nw-go1-extensions_gaps_many.xml",
        mode="vision_depth_act",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        render_type="depth",
        near_clip=0,
        far_clip=5,
        robot="go1",
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="nw-go2-gaps_many-vision_depth_act-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        xml_path="nw-go2-extensions_gaps_many.xml",
        mode="vision_depth_act",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        render_type="depth",
        near_clip=0,
        far_clip=5,
        robot="go2",
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-gaps_12in_226_blue_carpet_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_12in_226_blue_carpet_v2",
        xml_path=f"{prefix}-go1-gaps_12in_226_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-gaps_16in_226_blue_carpet_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_16in_226_blue_carpet_v2",
        xml_path=f"{prefix}-go1-gaps_16in_226_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-gaps_grassy_courtyard_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_grassy_courtyard_v2",
        xml_path=f"{prefix}-go1-gaps_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-gaps_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}-go1-gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-splat_rgb_act-gaps_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="splat_rgb_act",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}-go1-gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-vision_depth_act-gaps_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="vision_depth_act",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}-go1-gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-hurdle_226_blue_carpet_v3-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_226_blue_carpet_v3",
        xml_path=f"{prefix}-go1-hurdle_226_blue_carpet_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-hurdle_black_stone_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_black_stone_v1",
        xml_path=f"{prefix}-go1-hurdle_black_stone_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.8, # y limit: 1.2
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-hurdle_one_blue_carpet_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_one_blue_carpet_v2",
        xml_path=f"{prefix}-go1-hurdle_one_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.35, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-hurdle_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_stata_v1",
        xml_path=f"{prefix}-go1-hurdle_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.35, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-hurdle_stata_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_stata_v2",
        xml_path=f"{prefix}-go1-hurdle_stata_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.5, # y limit: 0.7
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-hurdle_three_grassy_courtyard_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_three_grassy_courtyard_v2",
        xml_path=f"{prefix}-go1-hurdle_three_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.4, # y limit: 0.6
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-ramp_aligned_blue_carpet_v4-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_aligned_blue_carpet_v4",
        xml_path=f"{prefix}-go1-ramp_aligned_blue_carpet_v4.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-ramp_bricks_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_bricks_v2",
        xml_path=f"{prefix}-go1-ramp_bricks_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-ramp_grass_v3-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_grass_v3",
        xml_path=f"{prefix}-go1-ramp_grass_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-ramp_spread_blue_carpet_v5-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_spread_blue_carpet_v5",
        xml_path=f"{prefix}-go1-ramp_spread_blue_carpet_v5.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-building_31_stairs_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="building_31_stairs_v1",
        xml_path=f"{prefix}-go1-building_31_stairs_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.6, # y limit: 0.8
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-real_hurdle_three_grassy_ally_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_hurdle_three_grassy_ally_v2",
        xml_path=f"{prefix}-go1-real_hurdle_three_grassy_ally_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.4, # y limit: 0.6
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-real_stair_02_bcs_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_02_bcs_v1",
        xml_path=f"{prefix}-go1-real_stair_02_bcs_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.7, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-real_stair_04_bcs_dusk-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_04_bcs_dusk",
        xml_path=f"{prefix}-go1-real_stair_04_bcs_dusk.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.7, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-real_stair_08_mc_afternoon_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_08_mc_afternoon_v1",
        xml_path=f"{prefix}-go1-real_stair_08_mc_afternoon_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-stairs_4_stairs2up_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_4_stairs2up_v1",
        xml_path=f"{prefix}-go1-stairs_4_stairs2up_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-stairs_36_backstairs_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_36_backstairs_v2",
        xml_path=f"{prefix}-go1-stairs_36_backstairs_v2.xml",
        n_proprio=53,
        x_noise=0.10, # x limit: 0.2
        y_noise=0.6, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-stairs_48_v3-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_48_v3",
        xml_path=f"{prefix}-go1-stairs_48_v3.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-wood_ramp_aligned_bricks_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_aligned_bricks_v1",
        xml_path=f"{prefix}-go1-wood_ramp_aligned_bricks_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-wood_ramp_aligned_grass_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_aligned_grass_v2",
        xml_path=f"{prefix}-go1-wood_ramp_aligned_grass_v2.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go1-heightmap-wood_ramp_offset_bricks_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_offset_bricks_v2",
        xml_path=f"{prefix}-go1-wood_ramp_offset_bricks_v2.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go1",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-gaps_12in_226_blue_carpet_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_12in_226_blue_carpet_v2",
        xml_path=f"{prefix}-go2-gaps_12in_226_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-gaps_16in_226_blue_carpet_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_16in_226_blue_carpet_v2",
        xml_path=f"{prefix}-go2-gaps_16in_226_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-gaps_grassy_courtyard_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_grassy_courtyard_v2",
        xml_path=f"{prefix}-go2-gaps_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-gaps_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}-go2-gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-splat_rgb_act-gaps_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="splat_rgb_act",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}-go2-gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-vision_depth_act-gaps_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="vision_depth_act",
        dataset_name="gaps_stata_v1",
        xml_path=f"{prefix}-go2-gaps_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-hurdle_226_blue_carpet_v3-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_226_blue_carpet_v3",
        xml_path=f"{prefix}-go2-hurdle_226_blue_carpet_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-hurdle_black_stone_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_black_stone_v1",
        xml_path=f"{prefix}-go2-hurdle_black_stone_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.8, # y limit: 1.2
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-hurdle_one_blue_carpet_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_one_blue_carpet_v2",
        xml_path=f"{prefix}-go2-hurdle_one_blue_carpet_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.35, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-hurdle_stata_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_stata_v1",
        xml_path=f"{prefix}-go2-hurdle_stata_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.35, # y limit: 0.5
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-hurdle_stata_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_stata_v2",
        xml_path=f"{prefix}-go2-hurdle_stata_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.5, # y limit: 0.7
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-hurdle_three_grassy_courtyard_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="hurdle_three_grassy_courtyard_v2",
        xml_path=f"{prefix}-go2-hurdle_three_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.4, # y limit: 0.6
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-ramp_aligned_blue_carpet_v4-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_aligned_blue_carpet_v4",
        xml_path=f"{prefix}-go2-ramp_aligned_blue_carpet_v4.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-ramp_bricks_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_bricks_v2",
        xml_path=f"{prefix}-go2-ramp_bricks_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-ramp_grass_v3-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_grass_v3",
        xml_path=f"{prefix}-go2-ramp_grass_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-ramp_spread_blue_carpet_v5-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="ramp_spread_blue_carpet_v5",
        xml_path=f"{prefix}-go2-ramp_spread_blue_carpet_v5.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.3, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-building_31_stairs_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="building_31_stairs_v1",
        xml_path=f"{prefix}-go2-building_31_stairs_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.6, # y limit: 0.8
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-real_hurdle_three_grassy_ally_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_hurdle_three_grassy_ally_v2",
        xml_path=f"{prefix}-go2-real_hurdle_three_grassy_ally_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.4, # y limit: 0.6
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-real_stair_02_bcs_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_02_bcs_v1",
        xml_path=f"{prefix}-go2-real_stair_02_bcs_v1.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.7, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-real_stair_04_bcs_dusk-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_04_bcs_dusk",
        xml_path=f"{prefix}-go2-real_stair_04_bcs_dusk.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.7, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-real_stair_08_mc_afternoon_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="real_stair_08_mc_afternoon_v1",
        xml_path=f"{prefix}-go2-real_stair_08_mc_afternoon_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-stairs_4_stairs2up_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_4_stairs2up_v1",
        xml_path=f"{prefix}-go2-stairs_4_stairs2up_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-stairs_36_backstairs_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_36_backstairs_v2",
        xml_path=f"{prefix}-go2-stairs_36_backstairs_v2.xml",
        n_proprio=53,
        x_noise=0.10, # x limit: 0.2
        y_noise=0.6, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-stairs_48_v3-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="stairs_48_v3",
        xml_path=f"{prefix}-go2-stairs_48_v3.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.8, # y limit: 1.0
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-wood_ramp_aligned_bricks_v1-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_aligned_bricks_v1",
        xml_path=f"{prefix}-go2-wood_ramp_aligned_bricks_v1.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-wood_ramp_aligned_grass_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_aligned_grass_v2",
        xml_path=f"{prefix}-go2-wood_ramp_aligned_grass_v2.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)

add_env(
    env_id=f"Neverwhere-go2-heightmap-wood_ramp_offset_bricks_v2-cones",
    entrypoint=entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="heightmap_splat",
        dataset_name="wood_ramp_offset_bricks_v2",
        xml_path=f"{prefix}-go2-wood_ramp_offset_bricks_v2.xml",
        n_proprio=53,
        x_noise=0.15, # x limit: 0.2
        y_noise=0.2, # y limit: 0.4
        spawn_x_rand=SPAWN_X_RAND,
        spawn_y_rand=SPAWN_Y_RAND,
        spawn_yaw_rand=SPAWN_YAW_RAND,
        splat_render_keys=["rgb"],
        use_cones=True,
        robot="go2",
    ),
)