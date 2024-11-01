from collections import defaultdict

import gym
import numpy as np
import re
from typing import List, Union

from neverwhere.utils.depth_util import invisibility


class SegmentationWrapper(gym.Wrapper):
    """
    Renders segmentation, grouping all objects with common name prefixes as one object.
    Anything not provided will be assumed as one class, being the background (value -1 in the output segmentation)
    Optionally generates the mask in and out of each group

    Args:
    return_masks: A list of the same length as groups, specifying whether to return the mask for each group.
                  Each group will return two masks, one in and one out.
    """

    def __init__(
        self,
        env,
        *,
        width=1280,
        height=768,
        camera_id="ego-rgb-render",
        groups: List[List[str]],
        return_masks: Union[None, List[bool]] = None,
        mask_sky=True,
        invisible_prefix=["trunk"],  # "ball*", "soccer*", "basketball*"],
        **rest,
    ):
        super().__init__(env)

        assert not return_masks or len(groups) == len(return_masks), "length mismatch."

        model = self.unwrapped.env.physics.model
        all_geom_names = [model.geom(i).name for i in range(model.ngeom)]

        self.invisible_objects = []
        for prefix in invisible_prefix:
            self.invisible_objects.extend([geom_name for geom_name in all_geom_names if geom_name.startswith(prefix)])

        self.env = env
        self.width = width
        self.height = height
        self.camera_id = camera_id
        self.groups = groups
        self.return_masks = return_masks
        self.mask_sky = mask_sky

        model = self.unwrapped.env.physics.model

        all_geom_names = [model.geom(i).name for i in range(model.ngeom)]
        self.grouped_ids = defaultdict(list)

        self.return_masks = return_masks
        for geom_name in all_geom_names:
            for group_id, group in enumerate(groups):
                for pattern in group:
                    compiled_pattern = re.compile(pattern)
                    if compiled_pattern.match(geom_name):
                        self.grouped_ids[group_id].append(all_geom_names.index(geom_name))
                        break

        # Precompute colors for each group, plus one for the background
        self.colors = np.random.randint(0, 255, (len(self.grouped_ids) + 1, 3), dtype=np.uint8)

    def step(self, action):
        obs, rew, done, info = self.env.step(action)

        physics = self.unwrapped.env.physics
        with invisibility(physics, self.invisible_objects):
            frame = self.render(
                segmentation=True,
                width=self.width,
                height=self.height,
                camera_id=self.camera_id,
            )

        segmented = np.ones((self.height, self.width), dtype=np.int32) * -1

        for group_id, group in self.grouped_ids.items():
            segmented[np.isin(frame[..., 0], group)] = group_id

        segmented_image = self.colors[segmented + 1]

        info["segmented"] = segmented
        info["segmented_img"] = segmented_image

        masks = defaultdict(list)
        if self.return_masks is False:
            return obs, rew, done, info
        elif self.return_masks is None:
            sky_mask_in = np.ones_like(segmented_image[..., 0], dtype=bool)
            for group_id in range(len(self.grouped_ids)):
                mask = segmented == group_id
                masks[group_id].append(mask)
                masks[group_id].append(~mask)
                if self.mask_sky:
                    sky_mask_in &= ~mask
            if self.mask_sky:
                masks["sky"].append(sky_mask_in)
                masks["sky"].append(~sky_mask_in)
        else:
            for group_id in range(len(self.grouped_ids)):
                if not self.return_masks[group_id]:
                    continue
                mask = segmented == group_id
                masks[group_id].append(mask)
                masks[group_id].append(~mask)

        info["masks"] = masks
        return obs, rew, done, info
