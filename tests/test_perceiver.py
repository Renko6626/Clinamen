"""Far-set complement, safe learned summary and strict shared initialization."""
import copy
import pytest
import torch
from conftest import small_cfg
from stgtrain.registry import FEATURIZERS, MODELS, load_builtins
from test_featurize_v8 import obs
load_builtins()


def config():
    return small_cfg(featurize={"name":"danger_topk_v9","frame":"static","dt":False,"k_lasers":8},
                     model={"name":"set_attn_v4","joint_sa_layers":1,"far_init_seed":1})


def build():
    cfg=config();f=FEATURIZERS.get('danger_topk_v9')(cfg)
    return cfg,f,MODELS.get('set_attn_v4')(cfg,f.spec())


def test_far_complement_reuses_near_selection_and_preserves_v8():
    cfg,f,net=build(); o=obs();o.bullets_mask[:]=True
    # Deliberately tie distances; identify selected objects by distinct velocity.
    o.bullets[...,:2]=o.player_xy[:,None]+torch.tensor([100.,0.])
    o.bullets[...,2]=torch.arange(o.bullets.shape[1])
    o.bullets[...,4]=2
    got=f(o)
    near_ids=(got['bullets'][0,:,2]*8).long()[got['bullets_mask'][0]]
    far_ids=(got['far_bullets'][0,:,2]*8).long()[got['far_bullets_mask'][0]]
    assert set(near_ids.tolist()).isdisjoint(far_ids.tolist())
    assert set(near_ids.tolist())|set(far_ids.tolist())==set(range(o.bullets.shape[1]))
    old=copy.deepcopy(cfg);old['featurize']['name']='danger_topk_v8';old['model']={'name':'set_attn_v3','density_enabled':False}
    ref=FEATURIZERS.get('danger_topk_v8')(old)(o)
    for key in ref:torch.testing.assert_close(got[key],ref[key],atol=0,rtol=0)
    assert 'density' not in net.requires()
    o.bullets_mask[:]=False;o.bullets_mask[:,:cfg['featurize']['k_bullets']]=True
    empty=f(o)
    assert not empty['far_bullets_mask'].any() and torch.count_nonzero(empty['far_bullets'])==0


def test_far_summary_empty_padding_permutation_and_two_step_learning():
    from stgtrain.models.far_perceiver import FarPerceiver
    torch.manual_seed(7);net=FarPerceiver(16,2,init_seed=1)
    x=torch.randn(2,20,5);mask=torch.rand(2,20)>.3
    assert torch.count_nonzero(net(x,mask))==0
    opt=torch.optim.Adam(net.parameters(),lr=.01)
    for step in range(2):
        opt.zero_grad(); loss=(net(x,mask)-torch.randn(2,16)).square().mean();loss.backward()
        if step==0:assert net.out.weight.grad.abs().sum()>0
        else:
            assert net.latents.grad.abs().sum()>0
            assert net.phi[0].weight.grad.abs().sum()>0
        opt.step()
    expected=net(x,mask)
    changed=torch.where(mask[...,None],x,torch.full_like(x,float('nan')))
    torch.testing.assert_close(net(changed,mask),expected)
    perm=torch.arange(19,-1,-1)
    torch.testing.assert_close(net(x[:,perm],mask[:,perm]),expected,atol=1e-5,rtol=1e-5)
    empty=net(changed,torch.zeros_like(mask));assert torch.isfinite(empty).all() and torch.count_nonzero(empty)==0
    with torch.autocast('cpu',dtype=torch.bfloat16):assert torch.isfinite(net(x,mask)).all()


def test_migration_keeps_shared_weights_optimizer_and_zero_start(tmp_path):
    from stgtrain.ppo import PPO
    from stgtrain.checkpoint import save_checkpoint
    from stgtrain.train import initialize_perceiver_from_checkpoint
    cfg,f,_=build();old=copy.deepcopy(cfg)
    old['featurize']['name']='danger_topk_v8';old['model'].pop('far_init_seed');old['model'].update(name='set_attn_v3',density_enabled=False)
    of=FEATURIZERS.get('danger_topk_v8')(old)
    torch.manual_seed(9);a=PPO(old,lambda:MODELS.get('set_attn_v3')(old,of.spec()),torch.device('cpu'));rng=torch.get_rng_state()
    torch.manual_seed(9);b=PPO(cfg,lambda:MODELS.get('set_attn_v4')(cfg,f.spec()),torch.device('cpu'))
    assert torch.equal(torch.get_rng_state(),rng)
    path=tmp_path/'source.pt';save_checkpoint(path,ppo=a,update=1000,env_steps=1000,cfg=old)
    info=initialize_perceiver_from_checkpoint(b,cfg,path)
    assert not b.optimizer.state and info['migration']['new_keys']
    for k,v in a.agent.state_dict().items():
        if not k.startswith(('model.density.','model.dens_proj.')):
            assert torch.equal(v,b.agent.state_dict()[k])
            assert torch.equal(v,b.agent_inference.state_dict()[k])
    o=obs();x=f(o); y=of(o)
    for v,w in zip(a.agent.model(y),b.agent.model(x)):torch.testing.assert_close(v,w,atol=0,rtol=0)
    incompatible=copy.deepcopy(cfg);incompatible['featurize']['k_lasers']=4
    with pytest.raises(ValueError,match='k_lasers'):initialize_perceiver_from_checkpoint(b,incompatible,path)


def test_real_ppo_loss_learns_far_branch():
    from stgtrain.ppo import PPO
    cfg,f,_=build();cfg['ppo']['amp']='bf16'
    ppo=PPO(cfg,lambda:MODELS.get('set_attn_v4')(cfg,f.spec()),torch.device('cpu'))
    o=obs();o.bullets_mask[:]=True;x=f(o)
    assert x['far_bullets_mask'].any()
    # The production update performs loss/backward/Adam, twice to cross the zero-output gate.
    for _ in range(2):
        x2={k:torch.cat([v,v],0) for k,v in x.items() if k in ppo.feature_keys}
        actions=torch.tensor([0,1])
        with torch.no_grad():_,lp,_,values=ppo.agent.get_action_and_value(x2,actions)
        stats=ppo._update(x2,actions,lp,torch.tensor([-1.,1.]),values+1.,values)
        assert all(torch.isfinite(v).all() for v in stats)
    far=ppo.agent.model.far
    assert far.out.weight.abs().sum()>0
    assert far.latents.grad is not None and far.latents.grad.abs().sum()>0


def test_perceiver_onnx_reads_nonzero_summary(tmp_path):
    from stgtrain.export_onnx import DeployWrapper, export_graph, input_names
    from test_export_v8 import build as old_build, inputs
    ort=pytest.importorskip('onnxruntime')
    cfg,o,_,_=old_build();cfg['featurize']['name']='danger_topk_v9';cfg['model']['name']='set_attn_v4'
    # Leave valid bullets outside the near set in both samples.
    cfg['featurize']['k_bullets']=2
    f=FEATURIZERS.get('danger_topk_v9')(cfg);net=MODELS.get('set_attn_v4')(cfg,f.spec()).eval()
    with torch.no_grad():net.far.out.weight.normal_(0,.02)
    assert f(o)['far_bullets_mask'].any()
    wrapper=DeployWrapper(cfg,net,bullets_rows=o.bullets.shape[1],enemies_rows=o.enemies.shape[1]).eval()
    path=export_graph(wrapper,inputs(o,0),tmp_path/'perceiver.onnx')
    session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
    ref=net(f(o))[0]
    for i in range(2):
        args=inputs(o,i)
        got=torch.from_numpy(session.run(['logits'],{n:a.numpy() for n,a in zip(input_names(cfg),args)})[0])
        torch.testing.assert_close(got,ref[i],atol=1e-5,rtol=1e-5)
