# neverwhere splat model, gsplat version: 1.4.0
# please use the modified version of gsplat
# pip install git+https://github.com/ziyc/gsplat.git@ziyu/dev
import numpy as np
import torch
from torch import Tensor, nn
from typing import Dict, List, Literal, Union, Optional, Tuple

from gsplat.rendering import rasterization
from neverwhere_envs.utils.gs_utils import DefaultStrategy

class RenderCfg:
    # Background color
    background_color = [1, 1, 1]
    # SH degree
    sh_degree = 3
    # Rasterization mode
    rasterize_mode: Literal["antialiased", "classic"] = "antialiased"
    # Render mode
    render_mode: Literal["RGB", "RGB+ED"] = "RGB+ED"
    # Camera model
    camera_model: Literal["pinhole", "ortho", "fisheye"] = "pinhole"
    # Near plane clipping distance
    near_plane: float = 0.01
    # Far plane clipping distance
    far_plane: float = 1e10
    # Strategy for GS densification
    strategy=DefaultStrategy(
        verbose=True,
        absgrad=True,
        grow_grad2d=0.0008,
    )
    # Use packed mode for rasterization, this leads to less memory usage but slightly slower.
    packed: bool = False
    # Use sparse gradients for optimization. (experimental)
    sparse_grad: bool = False

class Model(nn.Module):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.splats = nn.ParameterDict(
            {
                "means": nn.Parameter(torch.zeros(1, 3, device=device)),
                "scales": nn.Parameter(torch.zeros(1, 3, device=device)),
                "quats": nn.Parameter(torch.zeros(1, 4, device=device)),
                "sh0": nn.Parameter(torch.zeros(1, 1, 3, device=device)),
                "shN": nn.Parameter(torch.zeros(1, 15, 3, device=device)),
                "opacities": nn.Parameter(torch.zeros(1, device=device)),
            }
        )

    def load_ckpt(self, ckpt):  # type: ignore
        for k in self.splats.keys():
            self.splats[k].data = ckpt["splats"][k]
            
    def rasterize_splats(
        self,
        camtoworlds: Tensor,
        Ks: Tensor,
        width: int,
        height: int,
        masks: Optional[Tensor] = None,
        **kwargs,
    ) -> Tuple[Tensor, Tensor, Dict]:
        means = self.splats["means"]  # [N, 3]
        # quats = F.normalize(self.splats["quats"], dim=-1)  # [N, 4]
        # rasterization does normalization internally
        quats = self.splats["quats"]  # [N, 4]
        scales = torch.exp(self.splats["scales"])  # [N, 3]
        opacities = torch.sigmoid(self.splats["opacities"])  # [N,]

        colors = torch.cat([self.splats["sh0"], self.splats["shN"]], 1)  # [N, K, 3]

        render_colors, render_alphas, info = rasterization(
            means=means,
            quats=quats,
            scales=scales,
            opacities=opacities,
            colors=colors,
            viewmats=torch.linalg.inv(camtoworlds),  # [C, 4, 4]
            Ks=Ks,  # [C, 3, 3]
            width=width,
            height=height,
            packed=RenderCfg.packed,
            absgrad=(
                RenderCfg.strategy.absgrad
                if isinstance(RenderCfg.strategy, DefaultStrategy)
                else False
            ),
            sparse_grad=RenderCfg.sparse_grad,
            rasterize_mode=RenderCfg.rasterize_mode,
            distributed=False,
            camera_model=RenderCfg.camera_model,
            **kwargs,
        )
        if masks is not None:
            render_colors[~masks] = 0
        return render_colors, render_alphas, info

    @torch.no_grad()
    def get_simple_outputs(
        self,
        *,
        c2w: Tensor,
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

        if isinstance(c2w, np.ndarray):
            c2w = torch.tensor(c2w, device=self.device, dtype=torch.float32)

        if scale is not None:
            scale_mat = torch.tensor([scale, scale, scale, 1], device=self.device, dtype=torch.float32)
            scale_mat = torch.diag(scale_mat)
            c2w = scale_mat @ c2w

        background = torch.tensor(RenderCfg.background_color, device=self.device, dtype=torch.float32)
        
        # get camera matrices
        K = torch.tensor([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], device=self.device, dtype=torch.float32).reshape(3,3)
        # flip the z and y axes to align with gsplat conventions
        R_edit = torch.eye(4, device=self.device, dtype=c2w.dtype)
        R_edit[1,1] = -1
        R_edit[2,2] = -1
        c2w = c2w @ R_edit

        # forward
        renders, alphas, info = self.rasterize_splats(
            camtoworlds=c2w.unsqueeze(0),
            Ks=K.unsqueeze(0),
            width=width,
            height=height,
            sh_degree=RenderCfg.sh_degree,
            near_plane=RenderCfg.near_plane,
            far_plane=RenderCfg.far_plane,
            render_mode=RenderCfg.render_mode,
        )
        colors, depths = renders[..., 0:3], renders[..., 3:4]

        return {
            "rgb": colors.squeeze(0),
            "depth": depths.squeeze(0),
            "accumulation": alphas.squeeze(0),
            "background": background,
        }
