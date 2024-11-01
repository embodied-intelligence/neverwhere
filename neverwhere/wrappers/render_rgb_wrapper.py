import gym


class RenderRGBWrapper(gym.Wrapper):
    """
    Renders RGB image from the specified camera.
    """

    def __init__(
        self,
        env,
        *,
        width=1280,
        height=768,
        camera_id="ego_rgb",
        **_,
    ):
        super().__init__(env)

        self.env = env
        self.width = width
        self.height = height
        self.camera_id = camera_id

        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]

    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        frame = self.render(
            width=self.width,
            height=self.height,
            camera_id=self.camera_id,
        )

        info["render_rgb"] = frame
        return obs, rew, done, info
