import gym
import numpy as np


class RenderDepthWrapper(gym.Wrapper):
    """
    Renders normalized linear depth. This wrapper does NOT apply inversion as in RenderDepthWrapper.
    Output is normalized wrt the specified near and far.
    """

    def __init__(
        self,
        env,
        *,
        width=1280,
        height=768,
        camera_id="ego_rgb-render",
        near=0.0,
        far=5.0,
        **_,
    ):
        super().__init__(env)

        self.env = env
        self.width = width
        self.height = height
        self.camera_id = camera_id
        self.near = near
        self.far = far

        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]

    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        if "depth_frame" in info:
            frame = info["depth_frame"]
        else:
            frame = self.render(
                "depth",
                width=self.width,
                height=self.height,
                camera_id=self.camera_id,
            )
            info["depth_frame"] = frame

        # clip
        frame = np.clip(frame, self.near, self.far)

        # normalize
        frame = (frame - self.near) / (self.far - self.near)

        info["render_depth"] = frame
        return obs, rew, done, info
