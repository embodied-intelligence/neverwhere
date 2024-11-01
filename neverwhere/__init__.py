import os
from contextlib import contextmanager
from importlib import import_module

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
    import neverwhere.tasks.examples

    env_spec = ALL_ENVS.get(env_id)

    if env_spec is None:
        raise ModuleNotFoundError(
            f"Environment {env_id} is not found. You can choose between:\n{ALL_ENVS}."
        )

    entry_point = env_spec["entry_point"]
    _kwargs = env_spec.get("kwargs", {})
    _kwargs.update(kwargs)

    env = entry_point(**_kwargs)

    return env
