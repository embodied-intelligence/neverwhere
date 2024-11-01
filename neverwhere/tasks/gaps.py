from lucidsim import add_env
from lucidsim.tasks import parkour

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

TERRAIN_RAND_PARAMS = {
    "terrain_type": "gaps",
    "length": (0.35, 0.5),  # forward
    "width": (0.75, 1.5),  # sideways
}

add_env(
    env_id="Gaps-range-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="range",
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Gaps-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="depth",
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Gaps-cones-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="depth",
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)
add_env(
    env_id="Gaps-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Gaps-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        domain_rand=True,
    ),
)
add_env(
    env_id="Gaps-cones-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)
add_env(
    env_id="Gaps-cones-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        domain_rand=True,
    ),
)
add_env(
    env_id="Gaps-heightmap_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)
add_env(
    env_id="Gaps-cones-heightmap_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
        use_cones=True,
    ),
)
add_env(
    env_id="Gaps-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["platform"], ["table-1", "table-2", "table-3"]],
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Gaps-cones-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["platform", "table-1", "table-2", "table-3"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)
add_env(
    env_id="Gaps-cones-segmentation_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="segmentation",
        n_proprio=53,
        x_noise=0,
        y_noise=0.1,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
        groups=[["platform*", "table*"], ["cone*"]],
        use_cones=True,
    ),
)
add_env(
    env_id="Gaps-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="vision",
        groups=[["platform"], ["table-1", "table-2", "table-3"]],
        x_noise=0,
        y_noise=0.1,
    ),
)
add_env(
    env_id="Gaps-cones-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="vision",
        groups=[["platform", "table-1", "table-2", "table-3"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Gaps-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["platform", "table-1", "table-2", "table-3"]],
        x_noise=0,
        y_noise=0.1,
    ),
)

add_env(
    env_id="Gaps-cones-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["platform", "table-1", "table-2", "table-3"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
    ),
)

add_env(
    env_id="Gaps-cones-lucidsim_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="gaps.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["platform", "table-1", "table-2", "table-3"], ["cone*"]],
        x_noise=0,
        y_noise=0.1,
        use_cones=True,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)

# todo: Alan add additional environments for sampling
