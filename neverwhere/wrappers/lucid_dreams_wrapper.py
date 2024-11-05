import cv2
import gym
import numpy as np
import torch
import torchvision.transforms.v2 as T
from torch import TensorType


class LucidDreamsWrapper(gym.Wrapper):
    """
    This one does not do anything extra when stepping the environment.
    It only serves to prepare the vision input through the update_vision
    method.

    This is because we need to get the vision input from outside the env.
    """

    def __init__(
        self,
        env,
        width=80,
        height=45,
        compute_deltas=False,
        drop_last=False,
        stack_size=7,
        imagenet_pipe=True,
        device="cuda",
        render_type="rgb",
        **_,
    ):
        super().__init__(env)

        print(f"Extra info passed into TrackingVisionWrapper {_}")

        self.env = env
        self.device = device

        self.width = width
        self.height = height

        self.stack_size = stack_size

        # not used currently
        self.compute_deltas = compute_deltas
        self.drop_last = drop_last

        self.render_type = render_type
        self.resize_tf = T.Resize((height, width), interpolation=T.InterpolationMode.BILINEAR)

        pipeline = [
            self.resize_tf,
            T.ToImage(),
        ]
        if imagenet_pipe:
            pipeline += [
                T.ToDtype(torch.float32, scale=True),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        else:
            pipeline += [
                T.ToDtype(torch.float32, scale=False),
                T.Normalize(mean=[127.5], std=[255]),
            ]

        self.transform = T.Compose(pipeline)

        self.channels = 1 if self.render_type == "depth" else 3

        # self.frame_buffer = torch.zeros(
        #     (stack_size, height, width, self.channels),
        #     device=self.device,
        #     dtype=torch.uint8,
        # )

        self.frame_buffer = None

    def update_vision(self, frame):
        """
        Takes in frame of HWC, add to the frame buffer, and return the processed stack.
        """
        # resize the frame
        frame = cv2.resize(frame, (self.width, self.height))

        if self.render_type == "depth":
            if self.near_clip is not None and self.far_clip is not None:
                frame = np.clip(frame, self.near_clip, self.far_clip)

                frame = (frame - self.near_clip) / (self.far_clip - self.near_clip)

                frame = (frame[..., None] * 255).astype(np.uint8)

            assert frame.dtype == "uint8"

        frame = torch.from_numpy(frame).to(self.device)

        if self.frame_buffer is None:
            self.frame_buffer = frame[None, :].repeat(self.stack_size, 1, 1, 1)
        else:
            self.frame_buffer = torch.cat((self.frame_buffer[1:], frame[None, :]), dim=0)

        processed_input: TensorType["stack", "channels", "height", "width"] = self.frame_buffer.permute(0, 3, 1, 2).contiguous()
        processed_input = processed_input.to(self.device, non_blocking=True).contiguous()
        processed_input = self.transform(processed_input)

        if self.compute_deltas:
            processed_input[:-1] = processed_input[-1:] - processed_input[:-1]

        if self.drop_last:
            processed_input = processed_input[:-1]

        # flatten
        processed_input: TensorType["BxTxCxHxW"] = processed_input[None, ...]
        return processed_input

    def step(self, action):
        obs, rew, done, info = self.env.step(action)

        return obs, rew, done, info
