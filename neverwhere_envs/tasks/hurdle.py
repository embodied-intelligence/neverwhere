from lucidsim import add_env
from lucidsim.tasks import parkour

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

TERRAIN_RAND_PARAMS = dict(
    terrain_type="hurdle",
    width=(0.5, 1.5),
    height=(0.1, 0.2),
    spacing=(2.5, 3.0),
)

add_env(
    env_id="Hurdle-range-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="range",
        x_noise=0.1,
        y_noise=0.5,
        # **vars(Go1ParkourCfg.depth),
    ),
)
add_env(
    env_id="Hurdle-parkour_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="parkour_depth",
        x_noise=0.1,
        y_noise=0.5,
        # **vars(Go1ParkourCfg.depth),
    ),
)
add_env(
    env_id="Hurdle-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
    ),
)
add_env(
    env_id="Hurdle-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        domain_rand=True,
    ),
)
add_env(
    env_id="Hurdle-cones-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)
add_env(
    env_id="Hurdle-cones-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
        domain_rand=True,
    ),
)
add_env(
    env_id="Hurdle-heightmap_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)
add_env(
    env_id="Hurdle-cones-heightmap_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)

add_env(
    env_id="Hurdle-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["hurdle-1", "hurdle-2", "hurdle-3"]],
        x_noise=0.1,
        y_noise=0.5,
    ),
)
add_env(
    env_id="Hurdle-cones-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["hurdle*", "cone*"]],
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)
add_env(
    env_id="Hurdle-cones-segmentation_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="segmentation",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
        groups=[["hurdle*"], ["cone*"]],
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)
add_env(
    env_id="Hurdle-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="vision",
        x_noise=0.1,
        y_noise=0.5,
    ),
)

add_env(
    env_id="Hurdle-cones-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="vision",
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)

add_env(
    env_id="Hurdle-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["hurdle-1", "hurdle-2", "hurdle-3"]],
        x_noise=0.1,
        y_noise=0.5,
    ),
)
add_env(
    env_id="Hurdle-cones-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["hurdle*"], ["cone*"]],
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)
add_env(
    env_id="Hurdle-cones-lucidsim_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["hurdle*"], ["cone*"]],
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)

add_env(
    env_id="Hurdle-ls_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="hurdle.xml",
        mode="vision",
        x_noise=0.1,
        y_noise=0.5,
        width=80,
        height=45,
        render_type="depth",
        near_clip=None,  # 0.01,
        far_clip=None,  # 5.0,
        stack_size=2,
    ),
)

# todo: Alan add additional environments for sampling
