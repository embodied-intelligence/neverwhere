import gym
import numpy as np


class HistoryWrapper(gym.Wrapper):
    def __init__(self, env, *, history_len=10):
        super().__init__(env)
        self.env = env

        self.num_obs = 53
        self.num_history = history_len
        self.history_buf = np.zeros((1, history_len, self.num_obs))

    def step(self, action):
        # privileged information and observation history are stored in info
        obs, rew, done, info = self.env.step(action)
        obs, priv_obs = obs[: self.num_obs], obs[self.num_obs :]

        obs_np = np.array(obs)[None, ...]
        priv_obs_np = np.array(priv_obs)[None, ...]

        if self.unwrapped.env.task.step_counter < 2:
            # repeat obs to fill history buffer
            obs_history = np.repeat(obs_np, self.num_history + 1, axis=-1)
            obs_np[:, 6:8] = 0
            self.history_buf = np.repeat(obs_np, self.num_history, axis=0)[None, ...]
        else:
            obs_history = np.concatenate([obs_np, self.history_buf.reshape(1, -1)], axis=-1)

            obs_np[:, 6:8] = 0
            self.history_buf = np.concatenate([self.history_buf[:, 1:], obs_np[:, None, :]], axis=1)

        # add the privileged obs
        obs_history = np.concatenate([obs_history[:, : self.num_obs], priv_obs_np, obs_history[:, self.num_obs :]], axis=-1)

        return obs_history, rew, done, info

    def reset(self):
        obs = super().reset()

        # repeat obs to fill history buffer
        obs_np, priv_obs = obs[: self.num_obs], obs[self.num_obs :]

        obs_np = np.array(obs_np)[None, ...]
        priv_obs_np = np.array(priv_obs)[None, ...]

        obs_history = np.repeat(obs_np, self.num_history + 1, axis=-1)
        obs_np[:, 6:8] = 0
        self.history_buf = np.repeat(obs_np, self.num_history, axis=0)[None, ...]

        # concatenate one more
        obs_history = np.concatenate([obs_history[:, : self.num_obs], priv_obs_np, obs_history[:, self.num_obs :]], axis=-1)

        return obs_history
