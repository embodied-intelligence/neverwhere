from pprint import pformat
from warnings import warn

import gym
import numpy as np

from neverwhere.utils.utils import euler_from_quaternion_np

CONTACT_TERMINATION_THRESHOLD = 10


class ResetWrapper(gym.Wrapper):
    """
    Updates the done flag based on the current state of the environment.

    Checks for termination based on robot orientation
    """

    def __init__(
        self,
        env,
        check_contact_termination=True,
        **rest,
    ):
        super().__init__(env)

        self.check_contact_termination = check_contact_termination
        if rest:
            warn("received extra parameters:" + pformat(rest))
        self.env = env

    def step(self, action):
        obs, rew, done, info = self.env.step(action)

        physics = self.unwrapped.env.physics

        w_last = physics.base_quat
        roll, pitch, yaw = euler_from_quaternion_np(w_last)

        roll_cutoff = np.abs(roll) > 1.2
        pitch_cutoff = np.abs(pitch) > 1.2

        # check termination contacts
        contacts = physics._get_contacts()

        if self.check_contact_termination:
            for t_name in physics.TERMINATION_CONTACT_NAMES:
                assert t_name in contacts, f"Contact {t_name} not found in {contacts.keys()}"
                if np.linalg.norm(contacts[t_name]) > CONTACT_TERMINATION_THRESHOLD:
                    print(f"Termination contact {t_name} exceeded threshold. Resetting now.")
                    done = True
                    break

        done = done or roll_cutoff or pitch_cutoff

        return obs, rew, done, info
