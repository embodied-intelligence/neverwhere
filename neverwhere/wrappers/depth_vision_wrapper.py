from pprint import pformat
from warnings import warn

import gym
import torch
import torchvision

from lucidsim.utils.depth_util import z2r


class DepthVisionWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        *,
        camera_id="realsense",
        width=80,
        height=45,
        near_clip=0.28,
        far_clip=2.0,
        update_interval=5,
        use_range=False,  # when True, use
        device=None,
        **rest,
    ):
        super().__init__(env)
        if rest:
            warn("received extra parameters:" + pformat(rest))
        self.env = env

        self.width = width
        self.height = height
        self.near_clip = near_clip
        self.far_clip = far_clip
        self.camera_id = camera_id
        self.update_interval = update_interval
        self.use_range = use_range
        self.device = device

        self.resize_transform = torchvision.transforms.Resize(
            (self.height, self.width),
            interpolation=torchvision.transforms.InterpolationMode.BICUBIC,
        )

        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]

    @staticmethod
    def _crop_depth_image(depth):
        """Crop the depth image to the specified dimensions.

        Go from [1, 45, 80] -> [1, 43, 72]
        """
        return depth[:, :-2, 4:-4]

    def process_depth(self, frame):
        """
        Process the depth image by:
        1. Converting into meters [ already done in zed_node init_params]
        2. Invert
        2. Clip distances
        3. Resize
        4. Normalize
        """
        if frame is None:
            return None

        frame = self._crop_depth_image(frame)

        # clip
        frame = torch.clip(frame, self.near_clip, self.far_clip)
        frame = self.resize_transform(frame)

        frame = frame - self.near_clip
        frame /= self.far_clip - self.near_clip
        frame -= 0.5

        return frame

    def step(self, action):
        # info = {}
        obs, rew, done, info = self.env.step(action)
        if (self.unwrapped.env.task.step_counter % self.update_interval) == 0:
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

            # fov is read from XML.
            if self.use_range:
                frame, *_ = z2r(frame, fov=self.fovy, h=self.height, w=self.width)

            # use float32
            if self.device:
                frame = torch.from_numpy(frame.copy()).float().to(self.device)

            depth_image = self.process_depth(frame[None, ...])

            # todo: move all of these into obs
            # this is the last ego depth for the policy
            if self.use_range:
                info["range"] = depth_image
                # this is the raw range map at the current frame.
                info["range_frame"] = frame
            else:
                info["depth"] = depth_image

        return obs, rew, done, info
