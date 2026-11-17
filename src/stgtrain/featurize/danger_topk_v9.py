"""v8 near features plus the unselected valid bullet slots for a far-set summary."""
from __future__ import annotations

import torch
from torch import Tensor

from ..envwrap import RawObs
from ..registry import FEATURIZERS
from .danger_topk_v8 import DangerTopKV8


@FEATURIZERS.register("danger_topk_v9")
class DangerTopKV9(DangerTopKV8):
    def __init__(self, cfg: dict):
        super().__init__(cfg)
        if self.frame != "static" or self.dt:
            raise ValueError("danger_topk_v9 requires frame=static, dt=false")
        self.cap = int(cfg["env"]["bullets_cap"])
        self.density_enabled = False

    def spec(self) -> dict[str, tuple[int, ...]]:
        return {**super().spec(), "far_bullets": (self.cap, 5), "far_bullets_mask": (self.cap,)}

    def extra_bullet_features(self, obs: RawObs, relative: Tensor, idx: Tensor, selected: Tensor) -> dict[str, Tensor]:
        near = torch.zeros_like(obs.bullets_mask).scatter(1, idx, selected)
        mask = obs.bullets_mask & ~near
        raw = torch.cat([relative / 192.0, obs.bullets[..., 2:4] / 8.0,
                         obs.bullets[..., 4:5] / 8.0], dim=-1)
        return {"far_bullets": torch.where(mask[..., None], raw, torch.zeros_like(raw)),
                "far_bullets_mask": mask}
