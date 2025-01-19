from neverwhere import add_env
from neverwhere.tasks.parkour import entrypoint
from ml_logger.job import instr

# scenes available in "neverwhere_envs/scene_list.txt"
prefix = "nw"
SPAWN_X_RAND = 0.1
SPAWN_Y_RAND = 0.1
SPAWN_YAW_RAND = 0.1

entrypoint = instr(entrypoint, stack_size=7) # set stack size to 7 as default
lucidsim_entrypoint = instr(entrypoint, scene_version="lucidsim", stack_size=7)

robot_list = ["go1", "go2"]
mode_list = ["vision_depth_act", "heightmap_splat", "splat_rgb_act"]

add_env(
    env_id="Neverwhere-go1-splat_rgb_act-lucidsim_gaps_grassy_courtyard_v2",
    entrypoint=lucidsim_entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="splat_rgb_act",
        dataset_name="gaps_grassy_courtyard_v2",
        xml_path="gaps_grassy_courtyard_v2.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        spawn_x_rand=0.1,
        spawn_y_rand=0.1,
        spawn_yaw_rand=0.1,
        splat_render_keys=["rgb"],
        scene_version="lucidsim",
        use_cones=False,
    ),
)

add_env(
    env_id="Neverwhere-go1-splat_rgb_act-lucidsim_hurdle_226_blue_carpet_v3",
    entrypoint=lucidsim_entrypoint,
    kwargs=dict(
        check_contact_termination=True,
        mode="splat_rgb_act",
        dataset_name="hurdle_226_blue_carpet_v3",
        xml_path="hurdle_226_blue_carpet_v3.xml",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        img_memory_length=10,
        splat_render_keys=["rgb"],
        scene_version="lucidsim",
        use_cones=False,
    ),
)

for robot in robot_list:
    add_env(
        env_id=f"nw-{robot}-gaps_many-vision_depth_act-v1",
        entrypoint=entrypoint,
        kwargs=dict(
            check_contact_termination=True,
            xml_path=f"nw-{robot}-extensions_gaps_many.xml",
            mode="vision_depth_act",
            n_proprio=53,
            x_noise=0,
            y_noise=0.1,
            use_cones=False,
            render_type="depth",
            near_clip=0,
            far_clip=5,
            robot=robot,
            camera_id="ego-rgb",
        ),
    )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-gaps_16in_226_blue_carpet_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="gaps_16in_226_blue_carpet_v2",
                xml_path=f"{prefix}-{robot}-gaps_16in_226_blue_carpet_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3,  # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-gaps_16in_226_blue_carpet_v2_small_noise-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="gaps_16in_226_blue_carpet_v2",
                xml_path=f"{prefix}-{robot}-gaps_16in_226_blue_carpet_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.1,  # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-gaps_grassy_courtyard_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="gaps_grassy_courtyard_v2",
                xml_path=f"{prefix}-{robot}-gaps_grassy_courtyard_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3, # y limit: 0.5
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-gaps_stata_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="gaps_stata_v1",
                xml_path=f"{prefix}-{robot}-gaps_stata_v1.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3,  # y limit: 0.5
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_226_blue_carpet_v3-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_226_blue_carpet_v3",
                xml_path=f"{prefix}-{robot}-hurdle_226_blue_carpet_v3.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_226_blue_carpet_v3_small_noise-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_226_blue_carpet_v3",
                xml_path=f"{prefix}-{robot}-hurdle_226_blue_carpet_v3.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.1, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_black_stone_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_black_stone_v1",
                xml_path=f"{prefix}-{robot}-hurdle_black_stone_v1.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.8, # y limit: 1.2
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_one_blue_carpet_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_one_blue_carpet_v2",
                xml_path=f"{prefix}-{robot}-hurdle_one_blue_carpet_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.35, # y limit: 0.5
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_stata_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_stata_v1",
                xml_path=f"{prefix}-{robot}-hurdle_stata_v1.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.35, # y limit: 0.5
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_stata_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_stata_v2",
                xml_path=f"{prefix}-{robot}-hurdle_stata_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.5, # y limit: 0.7
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-hurdle_three_grassy_courtyard_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="hurdle_three_grassy_courtyard_v2",
                xml_path=f"{prefix}-{robot}-hurdle_three_grassy_courtyard_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.4, # y limit: 0.6
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-ramp_aligned_blue_carpet_v4-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="ramp_aligned_blue_carpet_v4",
                xml_path=f"{prefix}-{robot}-ramp_aligned_blue_carpet_v4.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-ramp_bricks_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="ramp_bricks_v2",
                xml_path=f"{prefix}-{robot}-ramp_bricks_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-ramp_grass_v3-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="ramp_grass_v3",
                xml_path=f"{prefix}-{robot}-ramp_grass_v3.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-ramp_spread_blue_carpet_v5-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="ramp_spread_blue_carpet_v5",
                xml_path=f"{prefix}-{robot}-ramp_spread_blue_carpet_v5.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.3, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-building_31_stairs_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="building_31_stairs_v1",
                xml_path=f"{prefix}-{robot}-building_31_stairs_v1.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.6, # y limit: 0.8
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-real_hurdle_three_grassy_ally_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="real_hurdle_three_grassy_ally_v2",
                xml_path=f"{prefix}-{robot}-real_hurdle_three_grassy_ally_v2.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.4, # y limit: 0.6
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-real_stair_02_bcs_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="real_stair_02_bcs_v1",
                xml_path=f"{prefix}-{robot}-real_stair_02_bcs_v1.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.7, # y limit: 1.0
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-real_stair_04_bcs_dusk-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="real_stair_04_bcs_dusk",
                xml_path=f"{prefix}-{robot}-real_stair_04_bcs_dusk.xml",
                n_proprio=53,
                x_noise=0,
                y_noise=0.7, # y limit: 1.0
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-real_stair_08_mc_afternoon_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="real_stair_08_mc_afternoon_v1",
                xml_path=f"{prefix}-{robot}-real_stair_08_mc_afternoon_v1.xml",
                n_proprio=53,
                x_noise=0.15, # x limit: 0.2
                y_noise=0.8, # y limit: 1.0
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-stairs_4_stairs2up_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="stairs_4_stairs2up_v1",
                xml_path=f"{prefix}-{robot}-stairs_4_stairs2up_v1.xml",
                n_proprio=53,
                x_noise=0.15, # x limit: 0.2
                y_noise=0.8, # y limit: 1.0
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-stairs_36_backstairs_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="stairs_36_backstairs_v2",
                xml_path=f"{prefix}-{robot}-stairs_36_backstairs_v2.xml",
                n_proprio=53,
                x_noise=0.10, # x limit: 0.2
                y_noise=0.6, # y limit: 1.0
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-stairs_48_v3-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="stairs_48_v3",
                xml_path=f"{prefix}-{robot}-stairs_48_v3.xml",
                n_proprio=53,
                x_noise=0.15, # x limit: 0.2
                y_noise=0.8, # y limit: 1.0
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-wood_ramp_aligned_bricks_v1-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="wood_ramp_aligned_bricks_v1",
                xml_path=f"{prefix}-{robot}-wood_ramp_aligned_bricks_v1.xml",
                n_proprio=53,
                x_noise=0.15, # x limit: 0.2
                y_noise=0.2, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-wood_ramp_aligned_grass_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="wood_ramp_aligned_grass_v2",
                xml_path=f"{prefix}-{robot}-wood_ramp_aligned_grass_v2.xml",
                n_proprio=53,
                x_noise=0.15, # x limit: 0.2
                y_noise=0.2, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )

for robot in robot_list:
    for mode in mode_list:
        add_env(
            env_id=f"Neverwhere-{robot}-{mode}-wood_ramp_offset_bricks_v2-cones",
            entrypoint=entrypoint,
            kwargs=dict(
                check_contact_termination=True,
                mode=mode,
                dataset_name="wood_ramp_offset_bricks_v2",
                xml_path=f"{prefix}-{robot}-wood_ramp_offset_bricks_v2.xml",
                n_proprio=53,
                x_noise=0.15, # x limit: 0.2
                y_noise=0.2, # y limit: 0.4
                spawn_x_rand=SPAWN_X_RAND,
                spawn_y_rand=SPAWN_Y_RAND,
                spawn_yaw_rand=SPAWN_YAW_RAND,
                splat_render_keys=["rgb"],
                use_cones=True,
                robot=robot,
            ),
        )