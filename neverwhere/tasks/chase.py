import os
from dm_control.rl import control
from dm_control.utils import containers
from gym_dmc.wrappers import FlattenObservation

from neverwhere.tasks import ROOT
from neverwhere.tasks.base.ball import Ball
from neverwhere.tasks.base.go1_base import Physics
from neverwhere.tasks.base.two_balls import Ball2
from neverwhere.wrappers.depth_midas_render_wrapper import MidasRenderDepthWrapper
from neverwhere.wrappers.domain_randomization_wrapper import DomainRandomizationWrapper
from neverwhere.wrappers.history_wrapper import HistoryWrapper
from neverwhere.wrappers.lucid_env import LucidEnv
from neverwhere.wrappers.optical_flow_wrapper import OpticalFlowWrapper
from neverwhere.wrappers.render_depth_wrapper import RenderDepthWrapper
from neverwhere.wrappers.render_rgb_wrapper import RenderRGBWrapper
from neverwhere.wrappers.reset_wrapper import ResetWrapper
from neverwhere.wrappers.scandots_wrapper import ScandotsWrapper
from neverwhere.wrappers.segmentation_wrapper import SegmentationWrapper
from neverwhere.wrappers.splat_wrapper import SplatWrapper
from neverwhere.wrappers.gsplat_wrapper import GSplatWrapper
from neverwhere.wrappers.transformer_observation_wrapper import TransformerObservationWrapper
from neverwhere.wrappers.vision_wrapper import TrackingVisionWrapper

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

SUITE = containers.TaggedTasks()

VALID_TARGETS = ["cone", "soccer", "basketball"]


def entrypoint(
    task_cls,
    xml_path,
    time_limit=DEFAULT_TIME_LIMIT,
    random=None,
    device=None,
    domain_rand=False,
    sampling_period=28,
    chase_target: VALID_TARGETS = "soccer",
    move_speed_range=[0.8, 0.8],
    # for camera frustum
    realsense_frustum=False,
    scene_version="neverwhere",
    **kwargs,
):
    # legacy support
    if "mode" in kwargs:
        kwargs.pop("mode")
        
    physics = Physics.from_xml_path(os.path.join(ROOT, xml_path))
    
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
    env = ScandotsWrapper(env, **kwargs, device=device)
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

    # NOTE(ziyu): in lucidsim, the 3dgs model is trained with nerfstudio's splatfacto
    # now we use gsplat's trainer, so we need to load the model in a different way
    # TODO(ziyu): in the future, we should unify the two ways of loading the model
    if scene_version == "lucidsim":
        env = SplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720,
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
    elif scene_version == "neverwhere":
        env = GSplatWrapper(
            env,
            camera_id="ego-rgb",
            width=1280,
            height=720, 
            device=device,
            fill_masks=fill_masks,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown data version: {scene_version}")
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

    return env