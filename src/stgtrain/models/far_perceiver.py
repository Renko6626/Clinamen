"""Eight learned latents read the fixed far-bullet table once, then mix and pool."""
from __future__ import annotations

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from .set_attn_v1 import SelfAttnBlock, layer_init


class FarPerceiver(nn.Module):
    def __init__(self, d: int, heads: int, *, init_seed: int = 1, ln_affine: bool = True):
        super().__init__()
        self.heads, self.dk = heads, d // heads
        # New-module initialization must not consume the shared policy's random stream.
        with torch.random.fork_rng(devices=[]):
            torch.default_generator.manual_seed(init_seed)
            self.latents = nn.Parameter(torch.randn(8, d) * 0.1)
            self.phi = nn.Sequential(layer_init(nn.Linear(5, d)), nn.ReLU(),
                                     layer_init(nn.Linear(d, d)), nn.ReLU())
            self.ln_q = nn.LayerNorm(d, elementwise_affine=ln_affine)
            self.ln_kv = nn.LayerNorm(d, elementwise_affine=ln_affine)
            self.ln_ff = nn.LayerNorm(d, elementwise_affine=ln_affine)
            self.q = layer_init(nn.Linear(d, d), std=1.0)
            self.kv = layer_init(nn.Linear(d, 2 * d), std=1.0)
            self.proj = layer_init(nn.Linear(d, d), std=1.0)
            self.ff = nn.Sequential(layer_init(nn.Linear(d, 2 * d)), nn.ReLU(),
                                    layer_init(nn.Linear(2 * d, d), std=1.0))
            self.sa = SelfAttnBlock(d, heads, ln_affine)
            self.out = nn.Linear(d, d)
            nn.init.zeros_(self.out.weight)
            nn.init.zeros_(self.out.bias)

    def forward(self, bullets: Tensor, mask: Tensor) -> Tensor:
        n, k, _ = bullets.shape
        x = torch.where(mask[..., None], bullets, torch.zeros_like(bullets))
        tokens = self.phi(x)
        d = self.heads * self.dk
        h = self.latents[None].expand(n, -1, -1).to(tokens.dtype)
        q = self.q(self.ln_q(h)).view(n, 8, self.heads, self.dk).transpose(1, 2)
        kk, vv = self.kv(self.ln_kv(tokens)).view(n, k, 2, self.heads, self.dk).permute(2, 0, 3, 1, 4)
        bias = (~mask).to(q.dtype)[:, None, None, :] * -1e4
        att = F.scaled_dot_product_attention(q, kk, vv, attn_mask=bias)
        h = h + self.proj(att.transpose(1, 2).reshape(n, 8, d))
        h = h + self.ff(self.ln_ff(h))
        h = self.sa(h, torch.ones(n, 8, device=mask.device, dtype=torch.bool))
        summary = self.out(h.mean(dim=1))
        return torch.where(mask.any(dim=1, keepdim=True), summary, torch.zeros_like(summary))
