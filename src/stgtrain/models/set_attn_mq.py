"""自机条件多查询读取联合威胁，摘要交流后展平进入策略主干。"""
from __future__ import annotations

from typing import Mapping

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from ..actions import NUM_ACTIONS
from ..registry import MODELS
from .set_attn_v1 import SelfAttnBlock, SetEncoder, layer_init, token_mlp
from .set_attn_v3 import SetAttnV3


class TokenEncoder(nn.Module):
    """复用逐实体MLP，仅生成token，不构造池化参数。"""

    def __init__(self, f_in: int, d: int):
        super().__init__()
        self.phi = token_mlp(f_in, d)

    def tokens(self, x: Tensor, mask: Tensor) -> Tensor:
        return self.phi(x) * mask[..., None]


class MultiQueryReadout(nn.Module):
    def __init__(self, d: int, heads: int, queries: int, sa_layers: int, ln_affine: bool = True):
        super().__init__()
        self.heads, self.dk = heads, d // heads
        self.seeds = nn.Parameter(torch.randn(queries, d) * 0.1)
        self.ctx = layer_init(nn.Linear(d, d), std=1.0)
        self.ln_q = nn.LayerNorm(d, elementwise_affine=ln_affine)
        self.ln_kv = nn.LayerNorm(d, elementwise_affine=ln_affine)
        self.q = layer_init(nn.Linear(d, d), std=1.0)
        self.kv = layer_init(nn.Linear(d, 2 * d), std=1.0)
        self.proj = layer_init(nn.Linear(d, d), std=1.0)
        self.ln_ff = nn.LayerNorm(d, elementwise_affine=ln_affine)
        self.ffn = nn.Sequential(layer_init(nn.Linear(d, 2 * d)), nn.ReLU(),
                                 layer_init(nn.Linear(2 * d, d), std=1.0))
        self.sa = nn.ModuleList(SelfAttnBlock(d, heads, ln_affine) for _ in range(sa_layers))

    def forward(self, tokens: Tensor, mask: Tensor, ctx: Tensor) -> Tensor:
        n, k, d = tokens.shape
        z = self.ctx(ctx)
        z = z[:, None, :] + self.seeds.to(z.dtype)[None, :, :]
        q = self.q(self.ln_q(z)).view(n, -1, self.heads, self.dk).transpose(1, 2)
        tokens = torch.where(mask[..., None], tokens, torch.zeros_like(tokens))
        kk, vv = self.kv(self.ln_kv(tokens)).view(n, k, 2, self.heads, self.dk).permute(2, 0, 3, 1, 4)
        bias = (~mask).to(q.dtype)[:, None, None, :] * -1e4
        att = F.scaled_dot_product_attention(q, kk, vv, attn_mask=bias)
        att = self.proj(att.transpose(1, 2).reshape(n, -1, d))
        # 全空时连输出投影bias也清零；查询残差仍携带自机条件。
        z = z + att * mask.any(dim=1)[:, None, None]
        z = z + self.ffn(self.ln_ff(z))
        query_mask = torch.ones(z.shape[:2], dtype=torch.bool, device=z.device)
        for block in self.sa:
            z = block(z, query_mask)
        return z


@MODELS.register("set_attn_mq")
class SetAttnMQ(SetAttnV3):
    """复用v3的threat_tokens/global_summary；独立构造实际使用的模块。"""

    def __init__(self, cfg: dict, spec: dict[str, tuple[int, ...]]):
        nn.Module.__init__(self)
        m = cfg["model"]
        self.player_token_enabled = m.get("player_token_enabled", False)
        if not isinstance(self.player_token_enabled, bool):
            raise ValueError("model.player_token_enabled must be boolean")
        if cfg["featurize"]["name"] != "danger_topk_v8":
            raise ValueError("set_attn_mq requires danger_topk_v8")
        if m.get("action_query", False) or not m.get("density_enabled", True):
            raise ValueError("set_attn_mq requires action_query=false, density_enabled=true")
        if int(m.get("sa_layers", 0)) or int(m.get("laser_sa_layers", 0)):
            raise ValueError("set_attn_mq uses joint_sa_layers; sa_layers/laser_sa_layers must be 0")
        d, heads, trunk = int(m["d"]), int(m["heads"]), int(m["trunk"])
        layers = int(m.get("joint_sa_layers", 1))
        queries, readout_layers = int(m.get("readout_queries", 4)), int(m.get("readout_sa_layers", 1))
        if d < 1 or heads < 1 or d % heads or queries < 1 or min(layers, readout_layers) < 0:
            raise ValueError("invalid set_attn_mq dimensions, queries or layers")
        self._spec = {k: tuple(spec[k]) for k in (
            "bullets", "bullets_mask", "lasers", "lasers_mask", "enemies", "enemies_mask",
            "density", "player", "cond")}
        affine = bool(m.get("ln_affine", True))
        self.ctx = nn.Sequential(layer_init(nn.Linear(spec["player"][0] + spec["cond"][0], d)), nn.ReLU())
        self.bullets = TokenEncoder(spec["bullets"][1], d)
        self.lasers = TokenEncoder(spec["lasers"][1], d)
        self.type_embedding = nn.Parameter(torch.randn(2, d) * 0.1)
        self.joint_sa = nn.ModuleList(SelfAttnBlock(d, heads, affine) for _ in range(layers))
        self.readout = MultiQueryReadout(d, heads, queries, readout_layers, affine)
        self.enemies = SetEncoder(spec["enemies"][1], d, heads, d)
        self.density_enabled = True
        self.density_fp32 = bool(m.get("density_fp32", False))
        c, h, w = spec["density"]
        self.density = nn.Sequential(
            layer_init(nn.Conv2d(c, 16, 3, padding=1)), nn.ReLU(),
            layer_init(nn.Conv2d(16, 16, 3, stride=2, padding=1)), nn.ReLU(), nn.Flatten())
        self.dens_proj = nn.Sequential(layer_init(nn.Linear(16 * ((h + 1) // 2) * ((w + 1) // 2), d)), nn.ReLU())
        self.trunk = nn.Sequential(layer_init(nn.Linear(queries * d + self.enemies.out_dim + 2 * d, trunk)),
                                   nn.ReLU(), layer_init(nn.Linear(trunk, trunk)), nn.ReLU())
        self.actor = layer_init(nn.Linear(trunk, NUM_ACTIONS), std=0.01)
        self.critic = layer_init(nn.Linear(trunk, 1), std=1.0)
        if self.player_token_enabled:
            self.player_type_embedding = nn.Parameter(torch.randn(d) * 0.1)

    def forward(self, feats: Mapping[str, Tensor]) -> tuple[Tensor, Tensor]:
        ctx = self.ctx(torch.cat([feats["player"], feats["cond"]], dim=-1))
        player_token = (ctx + self.player_type_embedding.to(ctx.dtype)
                        if self.player_token_enabled else None)
        tokens, mask = self.joint_tokens(feats, player_token)
        z = self.readout(tokens, mask, ctx).flatten(1)
        he = self.enemies(feats["enemies"], feats["enemies_mask"], ctx)
        hd = self.global_summary(feats, ctx)
        h = self.trunk(torch.cat([z, he, hd, ctx], dim=-1))
        return self.actor(h), self.critic(h).squeeze(-1)
