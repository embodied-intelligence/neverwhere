from typing import Literal

import cv2
import gym
import numpy as np
import torch
import torchvision.transforms.v2 as T
from torch import TensorType


class TrackingVisionWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        width=80,
        height=45,
        # for the depth render
        near_clip=0.0,
        far_clip=5,
        normalize_depth=True,
        render_type: Literal["depth", "rgb"] = "rgb",
        compute_deltas=False,
        drop_last=False,
        stack_size=1,
        # for the OG soda model
        flatten_stack=False,
        imagenet_pipe=False,
        camera_id="ego-rgb",
        device="cuda",
        channel_dim=None,
        **_,
    ):
        super().__init__(env)

        print(f"Extra info passed into TrackingVisionWrapper {_}")

        self.env = env
        self.device = device

        self.width = width
        self.height = height
        self.near_clip = near_clip
        self.far_clip = far_clip
        self.normalize_depth = normalize_depth
        self.render_type = render_type
        self.compute_deltas = compute_deltas
        self.drop_last = drop_last
        self.camera_id = camera_id

        self.stack_size = stack_size

        self.flatten = flatten_stack

        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]

        self.resize_tf = T.Resize((height, width), interpolation=T.InterpolationMode.BILINEAR)

        pipeline = [
            self.resize_tf,
            T.ToImage(),
        ]

        if channel_dim is not None:
            self.channels = channel_dim
        else:
            self.channels = 1 if self.render_type == "depth" else 3

        if imagenet_pipe:
            pipeline += [
                T.ToDtype(torch.float32, scale=True),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        else:
            pipeline += [
                T.ToDtype(torch.float32, scale=False),
                T.Normalize(mean=[127.5] * self.channels, std=[255] * self.channels),
                # T.Normalize(mean=[123.15, 138.13, 64.05], std=[44, 44, 44]),
            ]

        self.transform = T.Compose(pipeline)

        self.frame_buffer = None

    def process_frame(self, frame):
        if self.render_type == "depth":
            if self.near_clip is not None and self.far_clip is not None:
                frame = np.clip(frame, self.near_clip, self.far_clip)

                frame = (frame - self.near_clip) / (self.far_clip - self.near_clip)

                frame = (frame[..., None] * 255).astype(np.uint8)

            assert frame.dtype == "uint8"

        frame = torch.from_numpy(frame).to(self.device)

        if self.frame_buffer is None:
            # first step, fill with the frame
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

        if self.flatten:
            processed_input = processed_input.reshape(self.stack_size * self.channels, self.height, self.width)

        return processed_input

    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        # if (self.unwrapped.env.task.step_counter % 2) == 0:

        if self.render_type == "mask_in":
            frame = info["masks"][0][0]
            frame = (frame * 255).astype(np.uint8)
            # convert to RGB
            frame = np.stack((frame, frame, frame), axis=-1)
        elif self.render_type in ["depth", "rgb"]:
            frame = self.render(
                self.render_type,
                width=self.width,
                height=self.height,
                camera_id=self.camera_id,
            )
        elif self.render_type in ["splat_rgb", "splat_depth"]:
            frame = info[self.render_type]
            # resize to the desired size
            frame = cv2.resize(frame, (self.width, self.height))
        else:
            raise ValueError(f"Invalid render type {self.render_type}")
        frame = self.process_frame(frame)
        info["vision"] = frame[None, ...]

        return obs, rew, done, info
