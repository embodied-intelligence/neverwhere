from dm_control.rl import control
from gym_dmc.wrappers import FlattenObservation
from typing import Literal

from lucidsim import ChDir, add_env
from lucidsim.tasks import ROOT
from lucidsim.tasks.base.go1_base import Go1, Physics
from lucidsim.wrappers.depth_midas_render_wrapper import MidasRenderDepthWrapper
from lucidsim.wrappers.depth_vision_wrapper import DepthVisionWrapper
from lucidsim.wrappers.domain_randomization_wrapper import DomainRandomizationWrapper
from lucidsim.wrappers.history_wrapper import HistoryWrapper
from lucidsim.wrappers.lucid_dreams_wrapper import LucidDreamsWrapper
from lucidsim.wrappers.lucid_env import LucidEnv
from lucidsim.wrappers.optical_flow_wrapper import OpticalFlowWrapper
from lucidsim.wrappers.render_depth_wrapper import RenderDepthWrapper
from lucidsim.wrappers.render_rgb_wrapper import RenderRGBWrapper
from lucidsim.wrappers.reset_wrapper import ResetWrapper
from lucidsim.wrappers.scandots_wrapper import ScandotsWrapper
from lucidsim.wrappers.segmentation_wrapper import SegmentationWrapper
from lucidsim.wrappers.splat_wrapper import SplatWrapper
from lucidsim.wrappers.terrain_randomization_wrapper import TerrainRandomizationWrapper
from lucidsim.wrappers.transformer_observation_wrapper import TransformerObservationWrapper
from lucidsim.wrappers.vision_wrapper import TrackingVisionWrapper

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
    # note: we will remove the segmentation because it does not affect the
    #   policy. It is just what we allow the unroll script to collect.
    mode: Literal["heightmap", "vision", "depth", "segmentation", "heightmap_splat"],
    # waypoint randomization
    y_noise,
    x_noise,
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
    check_contact_termination=False,
    **kwargs,
):
    """Returns the Walk task."""
    with ChDir(ROOT):
        physics = Physics.from_xml_path(xml_path)

    if not use_cones:
        model = physics.model
        named_model = physics.named.model
        all_geom_names = [model.geom(i).name for i in range(model.ngeom)]
        # set transparency to 0
        for geom_name in all_geom_names:
            if geom_name.startswith("cone"):
                named_model.geom_rgba[geom_name] = [0, 0, 0, 0]

    task = Go1(vision=True, move_speed_range=move_speed_range, y_noise=y_noise, x_noise=x_noise, random=random, **kwargs)
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
    env = ResetWrapper(env, check_contact_termination=check_contact_termination)

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

    if mode == "range":
        env = DepthVisionWrapper(
            env,
            use_range=True,
            **kwargs,
            device=device,
        )
    elif mode == "parkour_depth":
        env = DepthVisionWrapper(
            env,
            use_range=False,
            **kwargs,
            device=device,
        )
    elif mode == "midas_depth":
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
            device=device,
        )
    elif mode == "render_depth":
        env = ScandotsWrapper(
            env,
            **kwargs,
            device=device,
        )
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
        )
    elif mode == "render_depth_realsense":
        env = ScandotsWrapper(
            env,
            **kwargs,
            device=device,
        )
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="realsense",
            near=0.28,
            far=2.0,
        )
    elif mode == "render_rgb":
        env = ScandotsWrapper(
            env,
            **kwargs,
            device=device,
        )
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
        )
        env = RenderRGBWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
        )
    elif mode == "vision":
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            **kwargs,
        )
    elif mode == "transformer_vision":
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            imagenet_pipe=False,
            **kwargs,
        )

    elif mode == "transformer_vision_sampling":
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
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )

    elif mode == "transformer_vision_splat":
        fill_masks = False
        if use_cones:
            # need seg and RGB
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

        env = SplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            render_type="splat_rgb",
            imagenet_pipe=False,
        )
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )
    elif mode == "transformer_vision_splat_realsense":
        fill_masks = False
        if use_cones:
            # need seg and RGB
            env = SegmentationWrapper(
                env,
                width=1280,
                height=720,
                camera_id="realsense-rgb",
                groups=[["soccer*", "basketball*", "ball*", "cone*"]],
                **kwargs,
            )
            env = RenderRGBWrapper(
                env,
                camera_id="realsense-rgb",
                width=1280,
                height=720,
                **kwargs,
            )
            fill_masks = True

        env = SplatWrapper(
            env,
            camera_id="realsense-rgb",
            width=1280,
            height=720,
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            render_type="splat_rgb",
            camera_id="realsense-rgb",
            imagenet_pipe=False,
        )
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )

    elif mode == "vision_depth_dagger":
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
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )

    elif mode == "vision_depth_realsense_dagger":
        # needed to keep track of the expert observations
        env = ScandotsWrapper(
            env,
            device=device,
        )
        env = TrackingVisionWrapper(
            env,
            device=device,
            stack_size=stack_size,
            camera_id="realsense",
            render_type="depth",
            near_clip=0.28,
            far_clip=2.0,
            **kwargs,
        )
        # for render depth
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="realsense",
            near=0.28,
            far=2.0,
        )
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )

    elif mode == "rgb":
        env = RenderRGBWrapper(
            env,
            camera_id="ego-rgb-render",
        )
    elif mode == "heightmap":
        env = ScandotsWrapper(env, **kwargs, device=device)
    elif mode == "heightmap_splat":
        env = ScandotsWrapper(env, **kwargs, device=device)
        fill_masks = False
        if use_cones:
            # need seg and RGB
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

        env = SplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
    elif mode == "vision_splat":
        fill_masks = False
        if use_cones:
            # need seg and RGB
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

        env = SplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
        env = TrackingVisionWrapper(
            env,
            camera_id="ego-rgb",
            render_type="splat_rgb",
            stack_size=stack_size,
            width=80,
            height=45,
            device=device,
            **kwargs,
        )
    elif mode == "segmentation":
        # pick these for the segmentation.
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)

        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            # near=0.01,
            # far=5.0,
            update_interval=1,
            device=device,
        )
        env = SegmentationWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            groups=groups,
            return_masks=return_masks,
            device=device,
        )
    elif mode == "flow":
        # pick these for the segmentation.
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = OpticalFlowWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            visualize=True,
            device=device,
        )
    elif mode == "lucidsim":
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            device=device,
        )
        env = SegmentationWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            groups=groups,
            return_masks=return_masks,
            device=device,
        )

    elif mode == "lucidsim_realsense":
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="realsense-rgb-render",
            device=device,
        )
        env = SegmentationWrapper(
            env,
            width=1280,
            height=768,
            camera_id="realsense-rgb-render",
            groups=groups,
            return_masks=return_masks,
            device=device,
        )

    elif mode == "lucidsim_dr":
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            device=device,
        )
        env = SegmentationWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            groups=groups,
            return_masks=return_masks,
            device=device,
        )
        env = RenderRGBWrapper(
            env,
            camera_id="ego-rgb-render",
            width=1280,
            height=768,
        )
    elif mode == "lucidsim_sampling":
        # lucidsim + sampling with the transformer policy
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            device=device,
        )
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
        )
        env = SegmentationWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
            groups=groups,
            return_masks=return_masks,
            device=device,
        )
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )
        env = LucidDreamsWrapper(
            env,
            width=80,
            height=45,
            stack_size=stack_size,
            imagenet_pipe=False,
        )
    elif mode == "lucidsim_sampling_realsense":
        # lucidsim + sampling with the transformer policy
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="realsense-rgb-render",
            device=device,
        )
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="realsense-rgb-render",
        )
        env = SegmentationWrapper(
            env,
            width=1280,
            height=768,
            camera_id="realsense-rgb-render",
            groups=groups,
            return_masks=return_masks,
            device=device,
        )
        env = TransformerObservationWrapper(
            env,
            stack_size=stack_size,
        )
        env = LucidDreamsWrapper(
            env,
            width=80,
            height=45,
            stack_size=stack_size,
            imagenet_pipe=False,
        )
    else:
        raise NotImplementedError(f"mode {mode} is not implemented.")

    return env


add_env(
    env_id="Parkour-range-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="range",
        x_noise=0.1,
        y_noise=0.5,
        # **vars(Go1ParkourCfg.depth),
    ),
)
add_env(
    env_id="Parkour-depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="depth",
        x_noise=0.1,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Parkour-segmentation-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["platform"], ["ramp-1", "ramp-2", "ramp-3"]],
        x_noise=0.1,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Parkour-cones-segmentation-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="segmentation",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        groups=[["platform*", "ramp*"], ["cone*"]],
        use_cones=True,
    ),
)
add_env(
    env_id="Parkour-cones-segmentation_randomize-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="segmentation",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        groups=[["platform*", "ramp*"], ["cone*"]],
        terrain_rand_params=TERRAIN_RAND_PARAMS,
        use_cones=True,
    ),
)
add_env(
    env_id="Parkour-flow-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="flow",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Parkour-heightmap-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Parkour-heightmap-dr-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        domain_rand=True,
    ),
)
add_env(
    env_id="Parkour-cones-heightmap-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        use_cones=True,
    ),
)
add_env(
    env_id="Parkour-cones-heightmap-dr-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        domain_rand=True,
    ),
)
add_env(
    env_id="Parkour-heightmap_randomize-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)
add_env(
    env_id="Parkour-cones-heightmap_randomize-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.1,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
        use_cones=True,
    ),
)
add_env(
    env_id="Parkour-vision-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="vision",
        x_noise=0.1,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Parkour-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["platform", "ramp-1", "ramp-2", "ramp-3"]],
        x_noise=0.1,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Parkour-cones-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["platform", "ramp-1", "ramp-2", "ramp-3"], ["cone*"]],
        x_noise=0.1,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Parkour-cones-lucidsim_randomize-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="parkour.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["platform", "ramp-1", "ramp-2", "ramp-3"], ["cone*"]],
        x_noise=0.1,
        y_noise=0.1,
        use_cones=True,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)
