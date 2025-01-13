from collections import deque

import cv2
import gym
import numpy as np
import torch


class ACTObservationWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        image_key="render_depth",
        width=320,
        height=180,
        device = "cuda" if torch.cuda.is_available() else "cpu",
        img_memory_length=1,
        **_,
    ):
        super().__init__(env)

        print(f"Extra info passed into ACTObservationWrapper {_}")

        self.env = env
        self.width = width
        self.height = height
        self.device = device

        self.image_key = image_key
        self.img_memory_length = img_memory_length

        self.img_history = None

        self.obs_buf = None

    def step(self, action):
        obs, rew, done, info = self.env.step(action)

        # for dagger
        info["teacher_obs"] = obs.copy()

        assert self.image_key in info, f"Key {self.image_key} should be rendered first"

        img = info[self.image_key]
        img_4x = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)
        if self.image_key == "render_depth":
            # add color channel 3
            img_4x = np.stack([img_4x] * 3, axis=-1)[None, None, ...]
        else:
            # put in 0-1
            img_4x = img_4x[None, None, ...] / 255.0

        # 1x1xchannelxhxw
        img_4x = img_4x.transpose(0, 1, 4, 2, 3)
        img_4x = torch.from_numpy(img_4x).float().to(self.device)
        # info["vision"] = img_4x

        if self.img_history is None:
            self.img_history = deque([img_4x] * self.img_memory_length, maxlen=self.img_memory_length)
        else:
            self.img_history.append(img_4x)

        img_input = torch.cat(list(self.img_history), dim=1)

        info["vision"] = img_input

        # obs[:, 53 : 53 + 132] = 0

        return obs, rew, done, info