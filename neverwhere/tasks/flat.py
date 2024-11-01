from lucidsim import add_env
from lucidsim.tasks import parkour

DEFAULT_TIME_LIMIT = 25

PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

add_env(
    env_id="Flat-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="depth",
        x_noise=0.1,
        y_noise=0.5,
    ),
)
add_env(
    env_id="Flat-cones-depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="depth",
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)
add_env(
    env_id="Flat-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
    ),
)
add_env(
    env_id="Flat-cones-heightmap-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)

add_env(
    env_id="Flat-cones-heightmap-dr-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="heightmap",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
        domain_rand=True,
    ),
)

add_env(
    env_id="Flat-heightmap_splat-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        mode="heightmap_splat",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
    ),
)

add_env(
    env_id="Flat-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["ground*"]],
        x_noise=0.1,
        y_noise=0.5,
    ),
)

add_env(
    env_id="Flat-cones-segmentation-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="segmentation",
        n_proprio=53,
        groups=[["ground*"], ["cone*"]],
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)
add_env(
    env_id="Flat-cones-segmentation_randomize-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="segmentation",
        n_proprio=53,
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
        groups=[["ground*"], ["cone*"]],
    ),
)
add_env(
    env_id="Flat-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="vision",
        x_noise=0.1,
        y_noise=0.5,
    ),
)
add_env(
    env_id="Flat-cones-vision-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="vision",
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)

add_env(
    env_id="Flat-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["ground*"]],
        x_noise=0.1,
        y_noise=0.5,
    ),
)

add_env(
    env_id="Flat-cones-lucidsim-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
        mode="lucidsim",
        n_proprio=53,
        groups=[["ground*"], ["cone*"]],
        x_noise=0.1,
        y_noise=0.5,
        use_cones=True,
    ),
)

add_env(
    env_id="Flat-ls_depth-v1",
    entrypoint=parkour.entrypoint,
    kwargs=dict(
        xml_path="flat.xml",
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
