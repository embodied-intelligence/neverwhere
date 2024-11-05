import numpy as np
import torch
import torch.nn.functional as F
from dm_control import mujoco
from torchtyping import TensorType
from typing import Tuple

ISAAC_DOF_NAMES = [
    "FL_hip_joint",
    "FL_thigh_joint",
    "FL_calf_joint",
    "FR_hip_joint",
    "FR_thigh_joint",
    "FR_calf_joint",
    "RL_hip_joint",
    "RL_thigh_joint",
    "RL_calf_joint",
    "RR_hip_joint",
    "RR_thigh_joint",
    "RR_calf_joint",
]

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]

UNITREE_DOF_NAMES = np.array([ISAAC_DOF_NAMES])[:, JOINT_IDX_MAPPING][0].tolist()


def pick(d, *keys, strict=False):
    """Pick keys"""
    _d = {}
    for k in keys:
        if k in d:
            _d[k] = d[k]
        elif strict:
            raise KeyError(k)
    return _d


def center_crop(img, new_width, new_height):
    """
    Crops the given NumPy image array to the specified width and height centered around the middle of the image.

    Parameters:
    img (numpy.ndarray): The image to be cropped (assumed to be in HxWxC format).
    new_width (int): The desired width of the cropped image.
    new_height (int): The desired height of the cropped image.

    Returns:
    numpy.ndarray: The cropped image.
    """

    height, width = img.shape[:2]

    # Calculate the starting points (top-left corner) of the crop
    start_x = (width - new_width) // 2
    start_y = (height - new_height) // 2

    # Perform the crop
    cropped_img = img[start_y : start_y + new_height, start_x : start_x + new_width]

    return cropped_img


def center_crop_pil(img, new_width, new_height):
    """
    Crops the given PIL Image to the specified width and height centered around the middle of the image.

    Parameters:
    img (PIL.Image.Image): The image to be cropped.
    new_width (int): The desired width of the cropped image.
    new_height (int): The desired height of the cropped image.

    Returns:
    PIL.Image.Image: The cropped image.
    """
    width, height = img.size

    # Calculate the top-left corner of the crop box
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    # Perform the crop
    cropped_img = img.crop((left, top, right, bottom))

    return cropped_img


def get_expanded_fov(expansion_factor, fov):
    """
    Compute the expanded field of view given the expansion factor and the original field of view.

    Expansion factor: the ratio of the new pixel width to the old pixel width.
    """

    fov_rad = np.deg2rad(fov)

    new_fov_rad = 2 * np.arctan(np.tan(fov_rad / 2) * expansion_factor)
    return np.rad2deg(new_fov_rad)


def warp_forward(x, flo, mode="bilinear"):
    """
    warp an image/tensor (im1) to im2, according to the optical flow
    x: [B, C, H, W] (im1)
    flo: [B, 2, H, W] flow (1 -> 2)
    """
    B, C, H, W = x.size()
    # mesh grid
    xx = torch.arange(0, W).view(1, -1).repeat(H, 1)
    yy = torch.arange(0, H).view(-1, 1).repeat(1, W)
    xx = xx.view(1, 1, H, W).repeat(B, 1, 1, 1)
    yy = yy.view(1, 1, H, W).repeat(B, 1, 1, 1)
    grid = torch.cat((xx, yy), 1).float()

    if x.is_cuda:
        grid = grid.cuda()
    # Invert the flow by multiplying by -1
    vgrid = grid - flo  # Change here
    # scale grid to [-1,1]
    vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :].clone() / max(W - 1, 1) - 1.0
    vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :].clone() / max(H - 1, 1) - 1.0

    vgrid = vgrid.permute(0, 2, 3, 1)
    output = F.grid_sample(x, vgrid, mode=mode)
    mask = torch.ones(x.size(), device=x.device)
    mask = F.grid_sample(mask, vgrid, mode=mode)

    mask[mask < 0.999] = 0
    mask[mask > 0] = 1

    return output


def euler_from_quaternion(
    quat_angle: TensorType["batch", 4],
) -> Tuple[TensorType["batch", 1]]:
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    x = quat_angle[:, 0]
    y = quat_angle[:, 1]
    z = quat_angle[:, 2]
    w = quat_angle[:, 3]
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = torch.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = torch.clip(t2, -1, 1)
    pitch_y = torch.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = torch.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z  # in radians


def euler_from_quaternion_np(quat_angle):
    """
    Convert a quaternion into Euler angles (roll, pitch, yaw) using NumPy.
    roll is rotation around x in radians (counterclockwise),
    pitch is rotation around y in radians (counterclockwise),
    yaw is rotation around z in radians (counterclockwise).
    """
    x, y, z, w = quat_angle

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x**2 + y**2)
    roll_x = np.arctan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = np.clip(t2, -1.0, 1.0)
    pitch_y = np.arcsin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y**2 + z**2)
    yaw_z = np.arctan2(t3, t4)

    return roll_x, pitch_y, yaw_z  # in radians


def quat_from_euler_xyz_np(roll, pitch, yaw):
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)

    qw = cy * cr * cp + sy * sr * sp
    qx = cy * sr * cp - sy * cr * sp
    qy = cy * cr * sp + sy * sr * cp
    qz = sy * cr * cp - cy * sr * sp

    return np.stack([qx, qy, qz, qw], axis=-1)


def smart_delta_yaw(yaw1, yaw2):
    # Calculate the difference
    delta = yaw2 - yaw1

    # Adjust differences to find the shortest path
    delta = (delta + torch.pi) % (2 * torch.pi) - torch.pi

    return delta


@torch.jit.script
def quat_rotate_inverse(q, v):
    shape = q.shape
    q_w = q[:, -1]
    q_vec = q[:, :3]
    a = v * (2.0 * q_w**2 - 1.0).unsqueeze(-1)
    b = torch.cross(q_vec, v, dim=-1) * q_w.unsqueeze(-1) * 2.0
    c = q_vec * torch.bmm(q_vec.view(shape[0], 1, 3), v.view(shape[0], 3, 1)).squeeze(-1) * 2.0
    return a - b + c


def quat_rotate_inverse_np(q, v):
    # Assuming q is of shape (4,) and v is of shape (3,)
    q_w = q[-1]  # Scalar
    q_vec = q[:3]  # Vector part of the quaternion (3,)

    # Calculate each component based on the quaternion rotation formula
    a = v * (2.0 * q_w**2 - 1.0)
    b = np.cross(q_vec, v) * q_w * 2.0
    c = q_vec * np.dot(q_vec, v) * 2.0

    # Combine the components
    result = a - b + c
    return result


def get_geom_speed(model, data, geom_name):
    """Returns the angular velocity of a geom."""
    geom_vel = np.zeros(6, dtype=np.float64)
    geom_type = mujoco.mjtObj.mjOBJ_GEOM
    geom_id = data.geom(geom_name).id
    mujoco.mj_objectVelocity(model, data, geom_type, geom_id, geom_vel, 0)
    return geom_vel[:3]


def get_vertical_fov(horizontal_fov, width, height):
    """
    For rectangular cameras

    :param horizontal_fov: expected to be in degrees
    :param width: px
    :param height: px
    :return: vertical FoV ( degrees )
    """

    horizontal_fov *= np.pi / 180

    aspect_ratio = width / height

    vertical_fov = 2 * np.arctan(np.tan(horizontal_fov / 2) / aspect_ratio)

    vertical_fov *= 180 / np.pi

    return vertical_fov


def sample_camera_frustum_batch(
    horizontal_fov: float,
    width: float,
    height: float,
    near: float,
    far: float,
    num_samples=1,
    horizontal_fov_min=None,
    random_state=None,
    **kwargs,
) -> Tuple[np.ndarray]:
    """
    For rectangular cameras, sample a point between near and far plane, relative to camera transform

    Output in view space: X forward, Y left, Z up

    (Assumed to have the same intrinsics for each sample)


    :param horizontal_fov: in degrees
    :param width: px
    :param height: px
    :param near: in meters (world units)
    :param far: in meters (world units)
    """

    vertical_fov = get_vertical_fov(horizontal_fov, width, height)
    vertical_fov = vertical_fov * np.pi / 180

    horizontal_fov = horizontal_fov * np.pi / 180

    if random_state is not None:
        dist = random_state.uniform(near, far, size=(num_samples, 1))  # distance
    else:
        dist = np.random.uniform(near, far, size=(num_samples, 1))  # distance

    if horizontal_fov_min is not None:
        horizontal_fov_min = horizontal_fov_min * np.pi / 180
        x_min = dist * np.tan(horizontal_fov_min / 2)
    else:
        x_min = 0.0

    y_range = dist * np.tan(vertical_fov / 2)

    if random_state is not None:
        y = random_state.uniform(-y_range, y_range, size=(num_samples, 1))
    else:
        y = np.random.uniform(-y_range, y_range, size=(num_samples, 1))

    x_range = dist * np.tan(horizontal_fov / 2)

    if random_state is not None:
        x = random_state.uniform(x_min, x_range, size=(num_samples, 1))
        x *= random_state.choice([-1, 1], size=(num_samples, 1))
    else:
        x = np.random.uniform(x_min, x_range, size=(num_samples, 1))
        x *= np.random.choice([-1, 1], size=(num_samples, 1))

    z = -dist

    x, y, z = -z, -x, -y

    # x = -z # forward
    # y = -x # left
    # z = -y # up

    return x, y, z


def quat_rotate_np(q, v):
    q_w = q[:, -1]  # Scalar part of quaternion for each batch
    q_vec = q[:, :3]  # Vector part of quaternion for each batch

    a = v * (2.0 * q_w[:, np.newaxis] ** 2 - 1.0)
    b = np.cross(q_vec, v) * q_w[:, np.newaxis] * 2.0
    c = q_vec * (q_vec * v[:, :, np.newaxis]).sum(axis=2) * 2.0

    return a + b + c


def normalize_np(quat):
    norm = np.linalg.norm(quat, axis=1, keepdims=True)
    return quat / norm


def quat_apply_np(quat, vec):
    # Ensure quat is in the shape (-1, 4) and vec is in the shape (-1, 3)
    quat = quat.reshape(-1, 4)
    vec = vec.reshape(-1, 3)

    # Separate the quaternion into xyz (vector part) and w (scalar part)
    xyz = quat[:, :3]
    w = quat[:, 3:].reshape(-1, 1)

    # Compute the cross product t = 2 * cross(xyz, vec)
    t = np.cross(xyz, vec) * 2

    # Compute the rotated vector
    # vec + w*t + cross(xyz, t)
    rotated_vec = vec + w * t + np.cross(xyz, t)

    # Return the rotated vector, reshaped back to the original vec shape
    return rotated_vec.reshape(vec.shape)


def quat_apply_yaw_np(quat, vec):
    quat_yaw = np.copy(quat).reshape(-1, 4)
    quat_yaw[:, :2] = 0.0  # Set the first three columns to zero, assuming w last
    quat_yaw = normalize_np(quat_yaw)  # Normalize the quaternion
    return quat_apply_np(quat_yaw, vec)  # Apply the quaternion rotation to the vector


@torch.jit.script
def normalize_t(x, eps: float = 1e-9):
    return x / x.norm(p=2, dim=-1).clamp(min=eps, max=None).unsqueeze(-1)


def quat_apply_yaw_t(quat, vec):
    quat_yaw = quat.clone().view(-1, 4)
    quat_yaw[:, :2] = 0.0
    quat_yaw = normalize_t(quat_yaw)
    return quat_apply_t(quat_yaw, vec)


@torch.jit.script
def quat_apply_t(a, b):
    shape = b.shape
    a = a.reshape(-1, 4)
    b = b.reshape(-1, 3)
    xyz = a[:, :3]
    t = xyz.cross(b, dim=-1) * 2
    return (b + a[:, 3:] * t + xyz.cross(t, dim=-1)).view(shape)


def get_expanded_fov(expansion_factor, fov):
    """
    Compute the expanded field of view given the expansion factor and the original field of view.

    Expansion factor: the ratio of the new pixel width to the old pixel width.
    """

    fov_rad = np.deg2rad(fov)

    new_fov_rad = 2 * np.arctan(np.tan(fov_rad / 2) * expansion_factor)
    return np.rad2deg(new_fov_rad)


if __name__ == "__main__":
    expansion_factor = 768 / 720
    fov = 89
    new_fov = get_expanded_fov(expansion_factor, fov)
