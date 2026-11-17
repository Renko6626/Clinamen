"""v3 shared policy with a far-set Perceiver in place of its density CNN."""
from __future__ import annotations

import copy
from typing import Mapping
from torch import Tensor

from ..registry import MODELS
from .far_perceiver import FarPerceiver
from .set_attn_v3 import SetAttnV3


@MODELS.register("set_attn_v4")
class SetAttnV4(SetAttnV3):
    def __init__(self, cfg: dict, spec: dict[str, tuple[int, ...]]):
        if cfg["featurize"]["name"] != "danger_topk_v9":
            raise ValueError("set_attn_v4 requires danger_topk_v9")
        shared = copy.deepcopy(cfg)
        shared["model"]["density_enabled"] = False
        super().__init__(shared, spec)
        del self.density, self.dens_proj
        self._spec.update({k: tuple(spec[k]) for k in ("far_bullets", "far_bullets_mask")})
        m = cfg["model"]
        self.far = FarPerceiver(int(m["d"]), int(m["heads"]),
                                init_seed=int(m.get("far_init_seed", 1)),
                                ln_affine=bool(m.get("ln_affine", True)))

    def global_summary(self, feats: Mapping[str, Tensor], ctx: Tensor) -> Tensor:
        return self.far(feats["far_bullets"], feats["far_bullets_mask"])
