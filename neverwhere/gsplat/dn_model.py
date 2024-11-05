import numpy as np
import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torchtyping import TensorType
from typing import Dict, List, Literal, Union


class RenderCfg:
    background_color = [1, 1, 1]

    sh_degree = 3
    rasterize_mode: Literal["antialiased", "classic"] = "classic"

    predict_normals = False


class Model(nn.Module):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.gauss_params = nn.ParameterDict(
            {
                "means": nn.Parameter(torch.zeros(1, 3, device=device)),
                "scales": nn.Parameter(torch.zeros(1, 3, device=device)),
                "quats": nn.Parameter(torch.zeros(1, 4, device=device)),
                "features_dc": nn.Parameter(torch.zeros(1, 3, device=device)),
                "features_rest": nn.Parameter(torch.zeros(1, 15, 3, device=device)),
                "opacities": nn.Parameter(torch.zeros(1, 1, device=device)),
            }
        )

    @property
    def normals(self):
        return self.gauss_params["normals"]

    @property
    def num_points(self):
        return self.means.shape[0]

    @property
    def means(self):
        return self.gauss_params["means"]

    @property
    def scales(self):
        return self.gauss_params["scales"]

    @property
    def quats(self):
        return self.gauss_params["quats"]

    @property
    def features_dc(self):
        return self.gauss_params["features_dc"]

    @property
    def features_rest(self):
        return self.gauss_params["features_rest"]

    @property
    def opacities(self):
        return self.gauss_params["opacities"]

    def load_state_dict(self, state_dict, **kwargs):  # type: ignore
        is_ddp_model_state = True
        model_state = {}
        for key, value in state_dict.items():
            if key.startswith("_model."):
                # remove the "_model." prefix from key
                model_state[key[len("_model.") :]] = value
                # make sure that the "module." prefix comes from DDP,
                # rather than an attribute of the model named "module"
                if not key.startswith("_model.module."):
                    is_ddp_model_state = False
        # remove "module." prefix added by DDP
        if is_ddp_model_state:
            model_state = {key[len("module.") :]: value for key, value in model_state.items()}

        # resize the parameters to match the new number of points
        self.step = 30000
        if "means" in model_state:
            # For backwards compatibility, we remap the names of parameters from
            # means->gauss_params.means since old checkpoints have that format
            for p in ["means", "scales", "quats", "features_dc", "features_rest", "opacities"]:
                model_state[f"gauss_params.{p}"] = model_state[p]
        newp = model_state["gauss_params.means"].shape[0]
        for name, param in self.gauss_params.items():
            old_shape = param.shape
            new_shape = (newp,) + old_shape[1:]
            self.gauss_params[name] = torch.nn.Parameter(torch.zeros(new_shape, device=self.device))
        super().load_state_dict(model_state, **kwargs)
        
    def load_state_dict_gsplat(self, state_dict, **kwargs):
        """Load state dict from gsplat training format.
        
        The gsplat training format has slightly different parameter names and shapes,
        so we need to map them to our format.
        """
        # Extract splats from state dict if needed
        if "splats" in state_dict:
            state_dict = state_dict["splats"]
            
        # Map gsplat parameter names to our format and handle shape differences
        model_state = {}
        
        # Handle means (same shape)
        if "means" in state_dict:
            model_state["gauss_params.means"] = state_dict["means"]
            
        # Handle scales (same shape)
        if "scales" in state_dict:
            model_state["gauss_params.scales"] = state_dict["scales"]
            
        # Handle quaternions (same shape)
        if "quats" in state_dict:
            model_state["gauss_params.quats"] = state_dict["quats"]
            
        # Handle opacities (shape: [N,] -> [N,1])
        if "opacities" in state_dict:
            opacities = state_dict["opacities"]
            if len(opacities.shape) == 1:
                opacities = opacities.unsqueeze(-1)
            model_state["gauss_params.opacities"] = opacities
            
        # Handle SH features
        if "sh0" in state_dict and "shN" in state_dict:
            # sh0 is DC term [N,3]
            model_state["gauss_params.features_dc"] = state_dict["sh0"].squeeze(1)
            # shN is rest of SH coeffs [N,15,3]
            model_state["gauss_params.features_rest"] = state_dict["shN"]
            
        # Resize parameters to match new number of points
        newp = model_state["gauss_params.means"].shape[0]
        for name, param in self.gauss_params.items():
            old_shape = param.shape
            new_shape = (newp,) + old_shape[1:]
            self.gauss_params[name] = torch.nn.Parameter(torch.zeros(new_shape, device=self.device))
        
        # Load the mapped state dict
        super().load_state_dict(model_state, **kwargs)

    @torch.no_grad()
    def get_simple_outputs(
        self,
        *,
        c2w: TensorType["3x4"],
        fx: float,
        fy: float,
        cx: float,
        cy: float,
        width: float,
        height: float,
        scale=None,
    ) -> Dict[str, Union[torch.Tensor, List[Tensor]]]:
        """Takes in a Ray Bundle and returns a dictionary of outputs.

        Args:
            ray_bundle: Input bundle of rays. This raybundle should have all the
            needed information to compute the outputs.

        Returns:
            Outputs of model. (ie. rendered colors)
        """
        from gsplat._torch_impl import quat_to_rotmat
        from gsplat.project_gaussians import project_gaussians
        from gsplat.rasterize import rasterize_gaussians
        from gsplat.sh import spherical_harmonics

        if isinstance(c2w, np.ndarray):
            c2w = torch.tensor(c2w, device=self.device, dtype=torch.float32)

        if scale is not None:
            scale_mat = torch.tensor([scale, scale, scale, 1], device=self.device, dtype=torch.float32)
            scale_mat = torch.diag(scale_mat)
            c2w = scale_mat @ c2w

        background = torch.tensor(RenderCfg.background_color, device=self.device, dtype=torch.float32)

        # shift the camera to center of scene looking at center
        R = c2w[:3, :3]  # 3 x 3
        T = c2w[:3, 3:4]  # 3 x 1

        # flip the z and y axes to align with gsplat conventions
        R_edit = torch.diag(torch.tensor([1, -1, -1], device=self.device, dtype=R.dtype))
        R = R @ R_edit
        # analytic matrix inverse to get world2camera matrix
        R_inv = R.T
        T_inv = -R_inv @ T
        viewmat = torch.eye(4, device=R.device, dtype=R.dtype)
        viewmat[:3, :3] = R_inv
        viewmat[:3, 3:4] = T_inv
        # calculate the FOV of the camera given fx and fy, width and height
        W, H = int(width), int(height)

        opacities_crop = self.opacities
        means_crop = self.means
        features_dc_crop = self.features_dc
        features_rest_crop = self.features_rest
        scales_crop = self.scales
        quats_crop = self.quats

        colors_crop = torch.cat((features_dc_crop[:, None, :], features_rest_crop), dim=1)

        BLOCK_WIDTH = 16  # this controls the tile size of rasterization, 16 is a good default
        self.xys, self.depths, self.radii, self.conics, self.comp, self.num_tiles_hit, cov3d = project_gaussians(
            # type: ignore
            means_crop,
            torch.exp(scales_crop),
            1,
            quats_crop / quats_crop.norm(dim=-1, keepdim=True),
            viewmat.squeeze()[:3, :],
            fx,
            fy,
            cx,
            cy,
            H,
            W,
            BLOCK_WIDTH,
            clip_thresh=1e-3,
        )  # type: ignore
        if (self.radii).sum() == 0:
            return {"rgb": background.repeat(int(height), int(width), 1)}

        if RenderCfg.sh_degree > 0:
            viewdirs = means_crop.detach() - c2w.detach()[..., :3, 3]  # (N, 3)
            viewdirs = viewdirs / viewdirs.norm(dim=-1, keepdim=True)
            n = RenderCfg.sh_degree
            rgbs = spherical_harmonics(n, viewdirs, colors_crop)
            rgbs = torch.clamp(rgbs + 0.5, min=0.0)  # type: ignore
        else:
            rgbs = torch.sigmoid(colors_crop[:, 0, :])

        assert (self.num_tiles_hit > 0).any()  # type: ignore

        # apply the compensation of screen space blurring to gaussians
        opacities = None
        if RenderCfg.rasterize_mode == "antialiased":
            opacities = torch.sigmoid(opacities_crop) * self.comp[:, None]
        elif RenderCfg.rasterize_mode == "classic":
            opacities = torch.sigmoid(opacities_crop)
        else:
            raise ValueError("Unknown rasterize_mode: %s", self.config.rasterize_mode)

        rgb, alpha = rasterize_gaussians(  # type: ignore
            self.xys,
            self.depths,
            self.radii,
            self.conics,
            self.num_tiles_hit,  # type: ignore
            rgbs,
            opacities,
            H,
            W,
            BLOCK_WIDTH,
            background=background,
            return_alpha=True,
        )  # type: ignore

        alpha = alpha[..., None]
        rgb = torch.clamp(rgb, max=1.0)  # type: ignore

        # depth image
        depth_im = rasterize_gaussians(  # type: ignore
            self.xys,
            self.depths,
            self.radii,
            self.conics,
            self.num_tiles_hit,
            self.depths[:, None].repeat(1, 3),
            opacities,
            H,
            W,
            BLOCK_WIDTH,
            background=torch.zeros(3, device=self.device),
        )[..., 0:1]
        depth_im = torch.where(alpha > 0, depth_im / alpha, depth_im.detach().max())

        # visible gaussians
        self.vis_indices = torch.where(self.radii > 0)[0]

        normals_im = torch.full(rgb.shape, 0.0)
        if RenderCfg.predict_normals:
            quats_crop = quats_crop / quats_crop.norm(dim=-1, keepdim=True)
            normals = F.one_hot(torch.argmin(scales_crop, dim=-1), num_classes=3).float()
            rots = quat_to_rotmat(quats_crop)
            normals = torch.bmm(rots, normals[:, :, None]).squeeze(-1)
            normals = F.normalize(normals, dim=1)
            viewdirs = -means_crop.detach() + c2w.detach()[..., :3, 3]
            viewdirs = viewdirs / viewdirs.norm(dim=-1, keepdim=True)
            dots = (normals * viewdirs).sum(-1)
            negative_dot_indices = dots < 0
            normals[negative_dot_indices] = -normals[negative_dot_indices]
            # convert normals from world space to camera space
            normals = normals @ c2w.squeeze(0)[:3, :3]
            normals_im: Tensor = rasterize_gaussians(  # type: ignore
                self.xys,
                self.depths,
                self.radii,
                self.conics,
                self.num_tiles_hit,
                normals,
                torch.sigmoid(opacities_crop),
                H,
                W,
                BLOCK_WIDTH,
            )
            # convert normals from [-1,1] to [0,1]
            normals_im = normals_im / normals_im.norm(dim=-1, keepdim=True)
            normals_im = (normals_im + 1) / 2

        return {
            "rgb": rgb,
            "depth": depth_im,
            "normal": normals_im,
            "accumulation": alpha,
            "background": background,
        }

    
if __name__ == "__main__":
    import pickle
    results = []

    objects = []
    with open("/home/exx/debug_poses.pkl", "rb") as f:
        while True:
            try:
                obj = pickle.load(f)
                objects.append(obj)
            except EOFError:
                break  # No more objects in file

    poses = torch.tensor([d["c2w"][:3, :].tolist() for d in objects], device="cpu", dtype=torch.float32)
    cameras = Cameras(fx=360.0, fy=360.0, cx=640.0, cy=360.0, width=1280, height=720, camera_to_worlds=poses)

    ckpt_path = "/home/exx/datasets/lucidsim_envs/building_31_stairs_v1/model.ckpt"
    model = Model(device="cuda")
    state_dict = torch.load(ckpt_path)["pipeline"]
    state_dict.keys()

    model.load_state_dict(state_dict, strict=False)
    model = model.eval()

    for i, pose in enumerate(poses):
        camera = Cameras(fx=360.0, fy=360.0, cx=640.0, cy=360.0, width=1280, height=720, camera_to_worlds=pose[None, ...]).to("cuda")
        render = model.get_outputs(camera)["rgb"]
        
        render_np = render.detach().cpu().numpy()
        results.append((render_np * 255).astype(np.uint8))
        
    from ml_logger import logger
    print(logger.get_dash_url())
    logger.save_video(results, "debug.mp4", fps=50)    
        
        

    outputs = model.get_simple_outputs(c2w=c2w, fx=fx, fy=fy, cx=cx, width=width, height=height)
    rgb = outputs["rgb"]

    from matplotlib import pyplot as plt

    plt.imshow(rgb.cpu())
    plt.show()
