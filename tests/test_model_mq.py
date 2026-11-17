"""MQ威胁读取：掩码隔离、集合排列不变性及可训练性。"""
import pytest
import torch

from conftest import small_cfg
from stgtrain.config import from_dict
from stgtrain.registry import FEATURIZERS, MODELS, load_builtins
from test_model_v2 import busy_obs

load_builtins()


def build(**model):
    cfg = small_cfg(
        featurize={"name": "danger_topk_v8", "frame": "static", "dt": False, "k_lasers": 8},
        model={"name": "set_attn_mq", "joint_sa_layers": 1,
               "readout_queries": 4, "readout_sa_layers": 1, **model},
    )
    feat = FEATURIZERS.get("danger_topk_v8")(cfg)
    torch.manual_seed(4)
    net = MODELS.get("set_attn_mq")(cfg, feat.spec())
    obs = busy_obs(n=2)
    obs.laser_start_len = torch.full_like(obs.lasers_mask, 400, dtype=torch.float32)
    return cfg, net, feat(obs)


@pytest.mark.parametrize("player_token", [False, True])
def test_padding_and_permutation_do_not_change_policy(player_token):
    _, net, f = build(player_token_enabled=player_token)
    expected = net(f)
    g = dict(f)
    for name in ("bullets", "lasers"):
        mask = f[name + "_mask"]
        g[name] = torch.where(mask[..., None], f[name], torch.full_like(f[name], float("nan")))
    for a, b in zip(expected, net(g)):
        torch.testing.assert_close(a, b)
    for name in ("bullets", "lasers"):
        perm = torch.arange(f[name].shape[1] - 1, -1, -1)
        g[name], g[name + "_mask"] = f[name][:, perm], f[name + "_mask"][:, perm]
    for a, b in zip(expected, net(g)):
        torch.testing.assert_close(a, b, atol=1e-5, rtol=1e-5)


@pytest.mark.parametrize("empty", [("bullets",), ("lasers",), ("bullets", "lasers")])
@pytest.mark.parametrize("player_token", [False, True])
def test_empty_threats_ignore_padding_and_remain_finite(empty, player_token):
    _, net, f = build(player_token_enabled=player_token)
    for name in empty:
        f[name + "_mask"][:] = False
    expected = net(f)
    assert expected[0].shape == (2, 18) and expected[1].shape == (2,)
    for name in empty:
        f[name] = torch.full_like(f[name], float("nan"))
    for a, b in zip(expected, net(f)):
        assert torch.isfinite(b).all()
        torch.testing.assert_close(a, b)


@pytest.mark.parametrize("amp", [False, True])
@pytest.mark.parametrize("player_token", [False, True])
def test_policy_gradients_reach_all_queries_and_encoders(amp, player_token):
    _, net, f = build(density_enabled=True, player_token_enabled=player_token)
    with torch.autocast("cpu", dtype=torch.bfloat16, enabled=amp):
        logits, value = net(f)
    assert torch.isfinite(logits).all() and torch.isfinite(value).all()
    (logits.logsumexp(-1).sum() + value.sum()).backward()
    for name, p in net.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), name
        # 公共key bias只给每行score加常数，softmax抵消后梯度可以为0。
        if p.ndim > 1:
            assert p.grad.abs().sum() > 0, name
    assert (net.readout.seeds.grad.abs().sum(-1) > 0).all()
    if player_token:
        assert net.player_type_embedding.grad.abs().sum() > 0


def test_player_token_conditions_joint_threat_representation():
    _, net, f = build(player_token_enabled=True)
    ctx = net.ctx(torch.cat([f["player"], f["cond"]], dim=-1))
    token = ctx + net.player_type_embedding
    h, mask = net.joint_tokens(f, token)
    changed, _ = net.joint_tokens(f, token + torch.linspace(-1, 1, token.shape[-1]))
    threats = torch.cat([f["bullets_mask"], f["lasers_mask"]], dim=1)
    assert h.shape[1] == threats.shape[1] + 1 and mask[:, -1].all()
    torch.testing.assert_close(mask[:, :-1], threats)
    assert not torch.allclose(h[:, :-1][threats], changed[:, :-1][threats])
    # The scene also changes the resulting player representation.
    no_bullets = dict(f, bullets=f["bullets"] + 0.7)
    other, _ = net.joint_tokens(no_bullets, token)
    assert not torch.allclose(h[:, -1], other[:, -1])


def test_disabled_player_token_loads_original_mq_state():
    _, original, f = build()
    _, explicit_off, _ = build(player_token_enabled=False)
    explicit_off.load_state_dict(original.state_dict(), strict=True)
    assert not hasattr(original, "player_type_embedding")
    for a, b in zip(original(f), explicit_off(f)):
        torch.testing.assert_close(a, b, atol=0, rtol=0)


def test_readout_uses_context_and_both_threat_types():
    _, net, f = build()
    ctx = net.ctx(torch.cat([f["player"], f["cond"]], dim=-1))
    bt, lt = net.threat_tokens(f)
    tokens = torch.cat([bt, lt], dim=1)
    mask = torch.cat([f["bullets_mask"], f["lasers_mask"]], dim=1)
    z = net.readout(tokens, mask, ctx)
    assert not torch.allclose(z, net.readout(tokens, mask, ctx + 0.5))
    expected = net(f)
    for name in ("bullets", "lasers"):
        changed = net(dict(f, **{name: f[name] + 0.7}))
        assert not torch.allclose(expected[0], changed[0])
        assert not torch.allclose(expected[1], changed[1])


@pytest.mark.parametrize("player_token", [False, True])
def test_model_state_round_trip(tmp_path, player_token):
    cfg, net, f = build(player_token_enabled=player_token)
    path = tmp_path / "model.pt"
    torch.save({"cfg": cfg, "model": net.state_dict()}, path)
    saved = torch.load(path, weights_only=False)
    restored = MODELS.get(saved["cfg"]["model"]["name"])(from_dict(saved["cfg"]), net.requires())
    restored.load_state_dict(saved["model"], strict=True)
    for a, b in zip(net(f), restored(f)):
        torch.testing.assert_close(a, b, atol=0, rtol=0)


@pytest.mark.parametrize("model", [
    {"readout_queries": 0}, {"readout_sa_layers": -1},
    {"action_query": True}, {"density_enabled": False},
    {"player_token_enabled": "true"},
])
def test_incompatible_readout_settings_rejected(model):
    with pytest.raises(ValueError):
        build(**model)
