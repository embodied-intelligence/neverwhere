"""Go1 Walker Domain."""

from dm_control.rl import control
from dm_control.utils import containers
from gym_dmc.wrappers import FlattenObservation
from typing import Literal

from lucidsim import ChDir, add_env
from lucidsim.tasks import ROOT
from lucidsim.tasks.base.ball import Ball
from lucidsim.tasks.base.go1_base import Physics
from lucidsim.tasks.base.two_balls import Ball2
from lucidsim.wrappers.depth_midas_render_wrapper import MidasRenderDepthWrapper
from lucidsim.wrappers.domain_randomization_wrapper import DomainRandomizationWrapper
from lucidsim.wrappers.history_wrapper import HistoryWrapper
from lucidsim.wrappers.lucid_env import LucidEnv
from lucidsim.wrappers.optical_flow_wrapper import OpticalFlowWrapper
from lucidsim.wrappers.render_depth_wrapper import RenderDepthWrapper
from lucidsim.wrappers.render_rgb_wrapper import RenderRGBWrapper
from lucidsim.wrappers.reset_wrapper import ResetWrapper
from lucidsim.wrappers.scandots_wrapper import ScandotsWrapper
from lucidsim.wrappers.segmentation_wrapper import SegmentationWrapper
from lucidsim.wrappers.splat_wrapper import SplatWrapper
from lucidsim.wrappers.transformer_observation_wrapper import TransformerObservationWrapper
from lucidsim.wrappers.vision_wrapper import TrackingVisionWrapper

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

SUITE = containers.TaggedTasks()

VALID_TARGETS = ["cone", "soccer", "basketball"]


def entrypoint(
    task_cls,
    xml_path,
    mode: Literal["heightmap", "vision", "depth", "segmentation"],
    time_limit=DEFAULT_TIME_LIMIT,
    random=None,
    device=None,
    domain_rand=False,
    sampling_period=28,
    chase_target: VALID_TARGETS = "soccer",
    move_speed_range=[0.8, 0.8],
    # for lucidsim vision
    stack_size=1,
    # for camera frustum
    realsense_frustum=False,
    **kwargs,
):
    with ChDir(ROOT):
        physics = Physics.from_xml_path(xml_path)

    task = task_cls(
        move_speed_range=move_speed_range,
        random=random,
        sampling_period=sampling_period,
        realsense=realsense_frustum,
        **kwargs,
    )
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
        check_contact_termination=False,
    )

    remove_geom_prefixes = [prefix for prefix in VALID_TARGETS if prefix != chase_target]

    model = physics.model
    named_model = physics.named.model
    all_geom_names = [model.geom(i).name for i in range(model.ngeom)]
    # set transparency to 0
    for geom_name in all_geom_names:
        for remove_geom_prefix in remove_geom_prefixes:
            if geom_name.startswith(remove_geom_prefix):
                named_model.geom_rgba[geom_name] = [0, 0, 0, 0]

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

    if mode == "vision":
        env = TrackingVisionWrapper(
            env,
            camera_id="ego-rgb",
            device=device,
            stack_size=stack_size,
            **kwargs,
        )
    elif mode == "vision_depth_realsense":
        env = TrackingVisionWrapper(
            env,
            camera_id="realsense",
            render_type="depth",
            near_clip=0.28,
            far_clip=2.0,
            device=device,
            stack_size=stack_size,
            **kwargs,
        )
    elif mode == "heightmap":
        env = ScandotsWrapper(env, **kwargs, device=device)
    elif mode == "render_depth":
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
        )
    elif mode == "render_depth_realsense":
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = RenderDepthWrapper(
            env,
            width=1280,
            height=720,
            camera_id="realsense",
            near=0.28,
            far=2.0,
        )
    elif mode == "heightmap_splat":
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = SegmentationWrapper(
            env,
            width=1280,
            height=720,
            camera_id="ego-rgb",
            groups=[["soccer*", "basketball", "ball*", "cone*"]],
            **kwargs,
        )
        env = RenderRGBWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            **kwargs,
        )
        env = SplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            **kwargs,
            device=device,
            fill_masks=True,
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
    elif mode == "vision_splat":
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
        env = SplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            device=device,
            fill_masks=True,
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
        groups = kwargs.pop("groups")
        return_masks = kwargs.pop("return_masks", None)

        env = ScandotsWrapper(env, **kwargs, device=device)
        env = MidasRenderDepthWrapper(
            env,
            width=1280,
            height=768,
            camera_id="ego-rgb-render",
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
        env = ScandotsWrapper(env, **kwargs, device=device)
        env = OpticalFlowWrapper(env, width=1280, height=768, camera_id="ego-rgb-render", visualize=True, device=device)
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
        env = RenderRGBWrapper(
            env,
            camera_id="ego-rgb-render",
            width=1280,
            height=768,
        )
        # env = OpticalFlowWrapper(
        #     env,
        #     width=1280,
        #     height=768,
        #     camera_id="ego-rgb-render",
        #     visualize=True,
        #     device=device,
        # )

        # todo: add flow
    else:
        raise NotImplementedError(f"mode {mode} is not implemented.")

    return env


add_env(
    "Chase-soccer-vision-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="vision",
        n_proprio=53,
        sampling_period=100,
        chase_target="soccer",
        flatten_stack=True,
    ),
)

add_env(
    "Chase-basketball-vision-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="vision",
        n_proprio=53,
        sampling_period=200,
        chase_target="basketball",
        flatten_stack=True,
    ),
)

add_env(
    "Chase-soccer-render_depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="render_depth",
        n_proprio=53,
        sampling_period=28,
        chase_target="soccer",
    ),
)

add_env(
    "Chase-soccer-render_depth_realsense-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="render_depth_realsense",
        n_proprio=53,
        sampling_period=28,
        chase_target="soccer",
        realsense_frustum=True,
    ),
)

add_env(
    "Chase-soccer-vision-5-depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="vision",
        n_proprio=53,
        sampling_period=100,
        chase_target="soccer",
        stack_size=5,
        flatten_stack=True,
        render_type="depth",
        channel_dim=3,
    ),
)

add_env(
    "Chase-cones-render_depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="render_depth",
        n_proprio=53,
        sampling_period=28,
        chase_target="cone",
    ),
)

add_env(
    "Chase-cones-render_depth_realsense-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="render_depth_realsense",
        n_proprio=53,
        sampling_period=28,
        chase_target="cone",
        realsense_frustum=True,
    ),
)

add_env(
    "Chase-cones-vision-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="vision",
        n_proprio=53,
        sampling_period=200,
        chase_target="cone",
        flatten_stack=True,
    ),
)

add_env(
    "Chase-cones-vision-5-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="vision",
        n_proprio=53,
        sampling_period=100,
        chase_target="cone",
        stack_size=5,
        flatten_stack=True,
    ),
)

add_env(
    "Chase-cones-vision-5-depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="vision",
        n_proprio=53,
        sampling_period=100,
        chase_target="cone",
        stack_size=5,
        flatten_stack=True,
        render_type="depth",
        channel_dim=3,
    ),
)

add_env(
    "Chase-two-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase_two.xml",
        task_cls=Ball2,
        mode="vision",
        n_proprio=53,
    ),
)

add_env(
    "Chase-heightmap-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        sampling_period=200,
    ),
)
add_env(
    "Chase-basketball-heightmap-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        chase_target="basketball",
    ),
)
add_env(
    "Chase-soccer-heightmap-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        chase_target="soccer",
    ),
)
add_env(
    "Chase-cones-heightmap-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        chase_target="cone",
    ),
)

add_env(
    "Chase-heightmap-dr-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
    ),
)

add_env(
    "Chase-heightmap-dr_5-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        randomize_every_n_steps=5,
    ),
)

add_env(
    env_id="Chase-cones-heightmap-dr_7-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="heightmap",
        task_cls=Ball,
        n_proprio=53,
        chase_target="cone",
        domain_rand=True,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Chase-cones-dr_7_sampling-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="transformer_vision_sampling",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        task_cls=Ball,
        chase_target="cone",
        use_cones=True,
        domain_rand=True,
        stack_size=7,
        randomize_every_n_steps=7,
    ),
)

add_env(
    "Chase-soccer-heightmap-dr-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        chase_target="soccer",
    ),
)
add_env(
    "Chase-basketball-heightmap-dr-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        chase_target="basketball",
    ),
)
add_env(
    "Chase-cones-heightmap-dr-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        chase_target="cone",
    ),
)

add_env(
    "Chase-soccer-heightmap-dr_5-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        chase_target="soccer",
        randomize_every_n_steps=5,
    ),
)
add_env(
    "Chase-basketball-heightmap-dr_5-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        chase_target="basketball",
        randomize_every_n_steps=5,
    ),
)
add_env(
    "Chase-cones-heightmap-dr_5-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        task_cls=Ball,
        mode="heightmap",
        n_proprio=53,
        domain_rand=True,
        chase_target="cone",
        randomize_every_n_steps=5,
    ),
)

add_env(
    "Chase-segmentation-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="segmentation",
        task_cls=Ball,
        n_proprio=53,
        groups=[["ball"]],
    ),
)

add_env(
    "Chase-cones-segmentation-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="segmentation",
        task_cls=Ball,
        n_proprio=53,
        groups=[["ball*", "cone*"]],
    ),
)

add_env(
    "Chase-basketball-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="lucidsim",
        task_cls=Ball,
        n_proprio=53,
        groups=[["ground*", "floor*"], ["soccer*", "basketball*", "ball", "cone*"]],
        # 2x per second
        sampling_period=28,
        chase_target="basketball",
    ),
)

add_env(
    "Chase-soccer-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="lucidsim",
        task_cls=Ball,
        n_proprio=53,
        groups=[["ground*", "floor*"], ["soccer*", "basketball*", "ball", "cone*"]],
        # 2x per second
        sampling_period=28,
        chase_target="soccer",
    ),
)

add_env(
    "Chase-soccer-two_mask-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="lucidsim",
        task_cls=Ball,
        n_proprio=53,
        groups=[["soccer*", "basketball*", "ball", "cone*"]],
        # 2x per second
        sampling_period=28,
        chase_target="soccer",
    ),
)

add_env(
    "Chase-cones-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="lucidsim",
        task_cls=Ball,
        n_proprio=53,
        groups=[["ground*", "floor*"], ["soccer*", "basketball*", "ball", "cone*"]],
        # 2x per second
        sampling_period=28,
        chase_target="cone",
    ),
)

add_env(
    "Chase-cones-two_mask-lucidsim-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path="chase.xml",
        mode="lucidsim",
        task_cls=Ball,
        n_proprio=53,
        groups=[["soccer*", "basketball*", "ball", "cone*"]],
        # 2x per second
        sampling_period=28,
        chase_target="cone",
    ),
)
