from lucidsim import add_env
from lucidsim.tasks import parkour

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

STAIRS_WH_RAND_PARAMS = {
    "terrain_type": "stairs_wh",
    "step_height": [0.12, 0.14],
    "step_length": [0.30, 0.35],
    "step_width": [2, 3],
}

add_env(
    env_id="Extensions-cones-parkour_spread_pillar-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread_pillar.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_spread_pillar-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread_pillar.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_spread_pillar-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread_pillar.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # imagenet_pipe=False,
        stack_size=7,
    ),
)

###

add_env(
    env_id="Extensions-cones-parkour_close_pillar-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close_pillar.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_close_pillar-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close_pillar.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_close_pillar-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close_pillar.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # #imagenet_pipe=False,
        stack_size=7,
    ),
)

###

add_env(
    env_id="Extensions-cones-parkour_spread-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_spread-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_spread-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_spread-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_spread.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # #imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_close-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_close-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_close-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-parkour_close-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_parkour_close.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*", "ramp*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        ##imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-curb-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_curb.xml",
        mode="depth",
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Extensions-curb-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_curb.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Extensions-curb-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_curb.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-curb-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_curb.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["ramp"]],
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-stairs_bcs-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="depth",
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Extensions-stairs_bcs-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Extensions-stairs_bcs-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_bcs-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_bcs-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)
add_env(
    env_id="Extensions-cones-stairs_bcs-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-stairs_bcs-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"]],
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_bcs-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_bcs.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-render_rgb-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="render_rgb",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-hurdle_one-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-heightmap-dr_7-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-dr_7_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="transformer_vision_sampling",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        stack_size=7,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-hurdle_one_14in-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one_14in-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one_14in.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        ##imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)
###

add_env(
    env_id="Extensions-cones-hurdle_one-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one_14in-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one_14in.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-hurdle_one-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-hurdle_one_14in-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one_14in.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        ##imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-dr_7-sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="transformer_vision_sampling",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        ##imagenet_pipe=False,
        domain_rand=True,
        stack_size=7,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        ##imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"], ["floor*", "ground*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-lucidsim_sampling_nostack-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        ##imagenet_pipe=False,
        stack_size=1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-lucidsim_sampling_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim_sampling_realsense",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        ##imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-lucidsim_sampling_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim_sampling_realsense",
        n_proprio=53,
        groups=[["step*"], ["floor*", "ground*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-parkour_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="parkour_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-hurdle_one-parkour_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="parkour_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-hurdle_one-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"]],
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        ##imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-hurdle_one-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        render_type="depth",
        ##imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one_10in-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one_10in.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-hurdle_one_10in-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one_10in.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one-vision_depth_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one.xml",
        mode="vision_depth_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_one_14in-vision_depth_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_one_14in.xml",
        mode="vision_depth_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

###

add_env(
    env_id="Extensions-cones-gaps_one-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-heightmap-dr_7-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-dr_7_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="transformer_vision_sampling",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # imagenet_pipe=False,
        domain_rand=True,
        stack_size=7,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-gaps_one-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-vision_depth_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="vision_depth_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-gaps_one-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-gaps_one-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"]],
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_one-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-gaps_one-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_one.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

###


add_env(
    env_id="Extensions-cones-gaps_many-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-gaps_many-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_many-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

# add_env(
#     env_id="Extensions-cones-gaps_many-render_depth-sampling-v1",
#     entrypoint=parkour.entrypoint,
#     kwargs=dict(
#         xml_path="extensions_gaps_many.xml",
#         mode="render_depth",
#         n_proprio=53,
#         x_noise=0,
#         y_noise=0.1,
#         use_cones=True,
#         terrain_rand_params=STAIRS_WH_RAND_PARAMS,
#         randomize
#     ),
# )

add_env(
    env_id="Extensions-gaps_many-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_many-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_many-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-gaps_many-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"]],
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-gaps_many-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-gaps_many-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_gaps_many.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

###

add_env(
    env_id="Extensions-cones-hurdle_many-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many_14in-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-vision_depth_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="vision_depth_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-hurdle_many-vision_depth_realsense_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="vision_depth_realsense_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-render_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="render_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-render_depth_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="render_depth_realsense",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-heightmap-dr_7-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["ground*", "floor*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-lucidsim_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="lucidsim_realsense",
        n_proprio=53,
        groups=[["step*"], ["ground*", "floor*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
    ),
)

add_env(
    env_id="Extensions-hurdle_many-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-hurdle_many_10in-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many_10in.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many_10in-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many_10in.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-hurdle_many_14in-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hurdle_many_14in.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)
###

add_env(
    env_id="Extensions-cones-stairs_wh-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-speed_range-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        move_speed_range=[0.4, 0.8],
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-heightmap-dr_7-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-dr_7_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="transformer_vision_sampling",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # imagenet_pipe=False,
        domain_rand=True,
        stack_size=7,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-stairs_wh-midas_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="midas_depth",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-transformer_vision_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-transformer_vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="transformer_vision",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="rgb",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-vision_depth_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="vision_depth_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        render_type="depth",
        # imagenet_pipe=False,
        near_clip=0,
        far_clip=5,
        stack_size=7,
        camera_id="ego-rgb",
    ),
)

add_env(
    env_id="Extensions-stairs_wh-render_depth_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="render_depth_realsense",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Extensions-stairs_wh-vision_depth_realsense_dagger-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="vision_depth_realsense_dagger",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-stairs_wh-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-lucidsim_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim_realsense",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-lucidsim_dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim_dr",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
        randomize_every_n_steps=7,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-lucidsim-randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        terrain_rand_params=STAIRS_WH_RAND_PARAMS,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-stairs_wh-lucidsim_sampling-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim_sampling",
        n_proprio=53,
        groups=[["step*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-lucidsim_sampling_realsense-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="lucidsim_sampling_realsense",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        # imagenet_pipe=False,
        stack_size=7,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-heightmap-randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        terrain_rand_params=STAIRS_WH_RAND_PARAMS,
    ),
)

add_env(
    env_id="Extensions-cones-stairs_wh-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_stairs_wh.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hallway-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hallway.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Extensions-cones-hallway-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="extensions_hallway.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["floor"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

# todo: Alan add additional environments for sampling
