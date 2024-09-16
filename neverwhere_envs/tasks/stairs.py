from lucidsim import add_env
from lucidsim.tasks import parkour

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

TERRAIN_RAND_PARAMS = {
    "spacing": (0.4, 0.75),
    "height": (0.15, 0.30),
    "width": (0.5, 1.0),
    "terrain_type": "stairs",
}

add_env(
    env_id="Stairs-range-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="range",
        x_noise=0,
        y_noise=0.2,
        # **vars(Go1ParkourCfg.depth),
    ),
)
add_env(
    env_id="Stairs-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="depth",
        x_noise=0,
        y_noise=0.2,
    ),
)
add_env(
    env_id="Stairs-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
    ),
)
add_env(
    env_id="Stairs-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        domain_rand=True,
    ),
)
add_env(
    env_id="Stairs-cones-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        domain_rand=True,
        use_cones=True,
    ),
)
add_env(
    env_id="Stairs-cones-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)
add_env(
    env_id="Stairs-heightmap_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)

add_env(
    env_id="Stairs-cones-heightmap_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0,
        y_noise=0.2,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
        use_cones=True,
    ),
)
add_env(
    env_id="Stairs-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["step-1", "step-2", "step-3", "step-4", "step-5"]],  # , ["cone-1", "cone-2", "cone-3"]],
        x_noise=0,
        y_noise=0.2,
    ),
)
add_env(
    env_id="Stairs-cones-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)
add_env(
    env_id="Stairs-cones-segmentation_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["step*"], ["cone*"]],
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)
add_env(
    env_id="Stairs-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="vision",
        x_noise=0,
        y_noise=0.2,
    ),
)

add_env(
    env_id="Stairs-cones-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="vision",
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
        # domain_rand=True,
    ),
)

add_env(
    env_id="Stairs-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="lucidsim",
        n_proprio=53,
        # groups=[["step-1", "step-2", "step-3"], ["cone-1", "cone-2", "cone-3"]],
        groups=[["step-1", "step-2", "step-3", "step-4", "step-5"]],
        x_noise=0,
        y_noise=0.2,
    ),
)

add_env(
    env_id="Stairs-cones-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="lucidsim",
        n_proprio=53,
        # groups=[["step-1", "step-2", "step-3"], ["cone-1", "cone-2", "cone-3"]],
        groups=[["step-1", "step-2", "step-3", "step-4", "step-5"], ["cone*"]],
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)
add_env(
    env_id="Stairs-cones-lucidsim-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="lucidsim",
        n_proprio=53,
        # groups=[["step-1", "step-2", "step-3"], ["cone-1", "cone-2", "cone-3"]],
        groups=[["step-1", "step-2", "step-3", "step-4", "step-5"], ["cone*"]],
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
    ),
)

add_env(
    env_id="Stairs-cones-lucidsim_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="stairs.xml",
        mode="lucidsim",
        n_proprio=53,
        # groups=[["step-1", "step-2", "step-3"], ["cone-1", "cone-2", "cone-3"]],
        groups=[["step-1", "step-2", "step-3", "step-4", "step-5"], ["cone*"]],
        x_noise=0,
        y_noise=0.2,
        use_cones=True,
        terrain_rand_params=TERRAIN_RAND_PARAMS,
    ),
)

# todo: Alan add additional environments for sampling
