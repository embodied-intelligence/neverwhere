import numpy as np
from dm_control.rl import control
from gym.spaces import Box
from gym_dmc.dmc_env import DMCEnv, convert_dm_control_to_gym_space


class LucidEnv(DMCEnv):
    def __init__(
        self,
        env: control.Environment,
        *,
        height: int = 84,
        width: int = 84,
        camera_id: int = 0,
        frame_skip: int = 1,
        channels_first: bool = True,
        from_pixels: bool = False,
        gray_scale: bool = False,
        warmstart: bool = True,  # info: https://github.com/deepmind/dm_control/issues/64
        no_gravity: bool = False,
        non_newtonian: bool = False,
        skip_start: int = None,  # useful in Manipulator for letting things settle
        space_dtype=None,  # default to float for consistency
    ):
        """LucidEnv Environment wrapper

        takes in an environment as the first argument, and wraps around it.

        Args:
            env ():
            height ():
            width ():
            camera_id ():
            frame_skip ():
            channels_first ():
            from_pixels ():
            gray_scale ():
            warmstart ():
            no_gravity ():
            non_newtonian ():
            skip_start ():
            space_dtype ():
        """
        # self.env = Env(**task_kwargs, environment_kwargs=environment_kwargs)
        self.env = env

        self.metadata = {
            "render.modes": ["human", "rgb_array"],
            "video.frames_per_second": round(1.0 / self.env.control_timestep()),
        }

        # deprecate, not needed.
        self.from_pixels = from_pixels
        self.gray_scale = gray_scale
        self.channels_first = channels_first

        obs_spec = self.env.observation_spec()
        if from_pixels:
            color_dim = 1 if gray_scale else 3
            image_shape = (
                [color_dim, width, height] if channels_first else [width, height, color_dim]
            )
            self.observation_space = convert_dm_control_to_gym_space(
                obs_spec,
                dtype=space_dtype,
                pixels=Box(low=0, high=255, shape=image_shape, dtype=np.uint8),
            )
        else:
            self.observation_space = convert_dm_control_to_gym_space(obs_spec, dtype=space_dtype)
        self.action_space = convert_dm_control_to_gym_space(
            self.env.action_spec(), dtype=space_dtype
        )
        self.viewer = None

        self.render_kwargs = dict(
            height=height,
            width=width,
            camera_id=camera_id,
        )
        self.frame_skip = frame_skip
        if not warmstart:
            self.env.physics.data.qacc_warmstart[:] = 0
        self.no_gravity = no_gravity
        self.non_newtonian = non_newtonian

        if self.no_gravity:  # info: this removes gravity.
            self.turn_off_gravity()

        self.skip_start = skip_start

    def reset(self, **kwargs):
        timestep = self.env.reset(**kwargs)
        obs = timestep.observation
        for i in range(self.skip_start or 0):
            obs = self.env.step([0]).observation

        if self.from_pixels:
            obs["pixels"] = self._get_obs_pixels()

        return obs
