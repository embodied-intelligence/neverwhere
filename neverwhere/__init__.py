import os
from contextlib import contextmanager
from importlib import import_module

# # register all envs
# from .tasks import chase, gaps, hurdle, parkour, stairs
#
# assert [gaps, hurdle, stairs, parkour, chase]


@contextmanager
def ChDir(dir):
    original_wd = os.getcwd()
    os.chdir(dir)
    print("changed work directory to", dir)
    try:
        yield
    finally:
        os.chdir(original_wd)
        print("now changed work directory back.")


ALL_ENVS = {}


def add_env(env_id, entrypoint, kwargs, strict=True):
    if strict and env_id in ALL_ENVS:
        raise RuntimeError(
            f"environment with id {env_id} has already been "
            f"registered. Set strict=False to overwrite."
        )
    ALL_ENVS[env_id] = {
        "entry_point": entrypoint,
        "kwargs": kwargs,
    }


def make(env_id: str, **kwargs):
    try:
        module_name, env_name = env_id.split(":")
    except ValueError:
        env_name = env_id
        module_name, *_ = env_id.split("-")
        module_name = module_name.lower()

    # relative to the lucidsim name space.
    import_module("lucidsim.tasks." + module_name)

    env_spec = ALL_ENVS.get(env_name)

    if env_spec is None:
        raise ModuleNotFoundError(
            f"Environment {env_id} is not found. You can choose between:\n{ALL_ENVS}."
        )

    entry_point = env_spec["entry_point"]
    _kwargs = env_spec.get("kwargs", {})
    _kwargs.update(kwargs)

    env = entry_point(**_kwargs)

    return env
