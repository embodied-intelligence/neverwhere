from params_proto import PrefixProto


class Go2ParkourCfg(PrefixProto, cli=False):
    class obs_scales(PrefixProto, cli=False):
        lin_vel = 2.0
        ang_vel = 0.25
        dof_pos = 1.0
        dof_vel = 0.05
        height_measurements = 5.0

    class init_state(PrefixProto, cli=False):
        pos = [0.0, 0.0, 0.42]  # x,y,z [m]
        default_joint_angles = {  # = target angles [rad] when action = 0.0
            "FL_hip_joint": 0.1,  # [rad]
            "RL_hip_joint": 0.1,  # [rad]
            "FR_hip_joint": -0.1,  # [rad]
            "RR_hip_joint": -0.1,  # [rad]

            "FL_thigh_joint": 0.8,  # [rad]
            "RL_thigh_joint": 1.0,  # [rad]
            "FR_thigh_joint": 0.8,  # [rad]
            "RR_thigh_joint": 1.0,  # [rad]
            
            "FL_calf_joint": -1.5,  # [rad]
            "RL_calf_joint": -1.5,  # [rad]
            "FR_calf_joint": -1.5,  # [rad]
            "RR_calf_joint": -1.5,  # [rad]
        }

    class depth(PrefixProto, cli=False):
        width = 80
        height=45
        # depth_size = (80, 45)
        near_clip = 0.28
        far_clip = 2.0

        # FOV is set in the xml file
        # horizontal_fov = 87

        camera_id = "realsense"

        update_interval = 5

    class control(PrefixProto):
        # PD Drive parameters:
        control_type = "P"
        stiffness_dict = {"joint": 30.0}  # [N*m/rad]
        damping_dict = {"joint": 0.6}  # [N*m*s/rad]
        action_scale = 0.25
        decimation = 4
        dt = 0.02
        clip_actions = 1.2
        clip_observations = 100.0

    class terrain(PrefixProto):
        flat_mask = False

    class heightmap(PrefixProto):
        measured_points_x = [
            -0.45,
            -0.3,
            -0.15,
            0,
            0.15,
            0.3,
            0.45,
            0.6,
            0.75,
            0.9,
            1.05,
            1.2,
        ]  # 1mx1.6m rectangle (without center line)
        measured_points_y = [
            -0.75,
            -0.6,
            -0.45,
            -0.3,
            -0.15,
            0.0,
            0.15,
            0.3,
            0.45,
            0.6,
            0.75,
        ]
        heightmap_height = 480
        heightmap_width = 480
        heightmap_fovy = 6
        cam_altitude = 25
        camera_id = "heightmap"


class Go2ParkourCfgCamera(PrefixProto):
    fps = 30
