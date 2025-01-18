import os
from dm_control.rl import control
from gym_dmc.wrappers import FlattenObservation
from typing import Literal

from neverwhere.tasks import ROOT
from neverwhere.wrappers.depth_midas_render_wrapper import MidasRenderDepthWrapper
from neverwhere.wrappers.depth_vision_wrapper import DepthVisionWrapper
from neverwhere.wrappers.act_observation_wrapper import ACTObservationWrapper
from neverwhere.wrappers.domain_randomization_wrapper import DomainRandomizationWrapper
from neverwhere.wrappers.history_wrapper import HistoryWrapper
from neverwhere.wrappers.lucid_env import LucidEnv
from neverwhere.wrappers.render_depth_wrapper import RenderDepthWrapper
from neverwhere.wrappers.render_rgb_wrapper import RenderRGBWrapper
from neverwhere.wrappers.reset_wrapper import ResetWrapper
from neverwhere.wrappers.scandots_wrapper import ScandotsWrapper
from neverwhere.wrappers.segmentation_wrapper import SegmentationWrapper
from neverwhere.wrappers.terrain_randomization_wrapper import TerrainRandomizationWrapper
from neverwhere.wrappers.vision_wrapper import TrackingVisionWrapper
from neverwhere.wrappers.pcd_wrapper import PointCloudWrapper

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

TERRAIN_RAND_PARAMS = {
    "terrain_type": "parkour",
    "tilt": (0.15, 0.45),
    "y_offset": (0.75, 1.0),
}


def entrypoint(
    xml_path,
    # waypoint randomization
    y_noise,
    x_noise,
    mode: Literal["vision_depth_act", "vision", "depth", "segmentation", "heightmap_splat"],
    # whether to add cones as visible geoms at waypoints
    use_cones=False,
    time_limit=DEFAULT_TIME_LIMIT,
    random=None,
    device=None,
    terrain_rand_params=None,
    domain_rand=False,
    move_speed_range=[0.8, 0.8],
    # for vision
    stack_size=1,
    img_memory_length=1,
    robot="go1",
    check_contact_termination=False,
    scene_version="neverwhere",
    **kwargs,
):
    """Returns the Walk task."""
     
    try:
        # NOTE(ziyu): fix for jaynes in lucidsim training, can be deleted
        if robot == "go1":
            from lucidsim.tasks.base.go1_base import Go1 as RobotModel
            from lucidsim.tasks.base.go1_base import Physics
        elif robot == "go2":
            from lucidsim.tasks.base.go2_base import Go2 as RobotModel
            from lucidsim.tasks.base.go2_base import Physics
        else:
            raise ValueError(f"Unknown robot: {robot}")
    except:
        if robot == "go1":
            from neverwhere.tasks.base.go1_base import Go1 as RobotModel
            from neverwhere.tasks.base.go1_base import Physics
        elif robot == "go2":
            from neverwhere.tasks.base.go2_base import Go2 as RobotModel
            from neverwhere.tasks.base.go2_base import Physics
        else:
            raise ValueError(f"Unknown robot: {robot}")
    
    # legacy support
    if "mode" in kwargs:
        kwargs.pop("mode")
        
    physics = Physics.from_xml_path(os.path.join(ROOT, xml_path))

    if not use_cones:
        model = physics.model
        named_model = physics.named.model
        all_geom_names = [model.geom(i).name for i in range(model.ngeom)]
        # set transparency to 0
        for geom_name in all_geom_names:
            if geom_name.startswith("cone"):
                named_model.geom_rgba[geom_name] = [0, 0, 0, 0]

    task = RobotModel(vision=True, move_speed_range=move_speed_range, y_noise=y_noise, x_noise=x_noise, random=random, **kwargs)
    env = control.Environment(
        physics,
        task,
        time_limit=time_limit,
        control_timestep=CONTROL_TIMESTEP,
        flat_observation=True,
    )
    env = LucidEnv(env)
    env = FlattenObservation(env)
    env = HistoryWrapper(env, history_len=10)
    env = ResetWrapper(
        env,
        check_contact_termination=check_contact_termination
    )

    if domain_rand:
        env = DomainRandomizationWrapper(
            env,
            randomize_color=True,
            randomize_lighting=True,
            randomize_camera=False,
            randomize_dynamics=False,
            seed=random,
            **kwargs,
        )
        env = RenderRGBWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
        )

    if terrain_rand_params is not None:
        terrain_type = terrain_rand_params.pop("terrain_type")
        env = TerrainRandomizationWrapper(env, terrain_type=terrain_type, rand_params=terrain_rand_params, random=random)
    
    # NOTE(ziyu): in lucidsim, the 3dgs model is trained with nerfstudio's splatfacto
    # now we use gsplat's trainer, so we need to load the model in a different way
    # TODO(ziyu): in the future, we should unify the two ways of loading the model
    if scene_version == "neverwhere":
        from neverwhere.wrappers.gsplat_wrapper import GSplatWrapper
        GS_wrapper = GSplatWrapper
    elif scene_version == "lucidsim":
        from neverwhere.wrappers.splat_wrapper import SplatWrapper
        GS_wrapper = SplatWrapper
    else:
        raise ValueError(f"Unknown data version: {scene_version}")
    
    if mode == "heightmap_splat":
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
            device=device,
        )
        fill_masks = False
        if use_cones: # need seg and RGB
            env = SegmentationWrapper(
                env,
                width=1280,
                height=720,
                camera_id="ego-rgb",
                groups=[["soccer*", "basketball*", "ball*", "cone*"]],
                **kwargs,
            )
            env = RenderRGBWrapper(
                env,
                camera_id="ego-rgb",
                width=1280,
                height=720,
                **kwargs,
            )
            fill_masks = True
        env = GS_wrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720, 
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
        # env = PointCloudWrapper(
        #     env,
        #     camera_id="tracking-pcd",
        #     width=1280,
        #     height=720, 
        #     lidar_width=640,
        #     lidar_height=360,
        #     lidar_camera_ids=["lidar0"],
        #     range_threshold=10,
        # )
        # env = TrackingVisionWrapper(
        #     env,
        #     camera_id="ego-rgb",
        #     render_type="splat_rgb",
        #     stack_size=stack_size,
        #     width=80,
        #     height=45,
        #     device=device,
        #     **kwargs,
        # )
    elif mode == "vision_depth_act":
        # needed to keep track of the expert observations
        env = ScandotsWrapper(
            env,
            device=device,
        )
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            **kwargs,
        )
        # for render depth
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
        )
        env = ACTObservationWrapper(
            env,
            image_key="render_depth",
            img_memory_length = img_memory_length,
            **kwargs,
        )
    elif mode == "splat_rgb_act":
        # needed to keep track of the expert observations
        env = ScandotsWrapper(
            env,
            device=device,
        )
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            **kwargs,
        )
        # for render depth
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
        )
        fill_masks = False
        if use_cones: # need seg and RGB
            env = SegmentationWrapper(
                env,
                width=1280,
                height=720,
                camera_id="ego-rgb",
                groups=[["soccer*", "basketball*", "ball*", "cone*"]],
                **kwargs,
            )
            env = RenderRGBWrapper(
                env,
                camera_id="ego-rgb",
                width=1280,
                height=720,
                **kwargs,
            )
            fill_masks = True
        env = GS_wrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720, 
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
        env = ACTObservationWrapper(
            env,
            image_key="splat_rgb",
            img_memory_length = img_memory_length,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return env