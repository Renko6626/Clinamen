# Magnus 训练迁移记录（2026-09-23 起）

Magnus（北大站点）上用 A100 跑训练，替代在 Vast.ai 租卡。本文保留迁移时的环境证据，维护 Job 入口、版本兼容和 wheel 来源；简要流程见[启动概况](agent-memory/training-workflow.md)，当前研究安排见[下一步](next-steps.md)，吞吐数据见[性能记录](perf-baseline.md)。

## 环境要求

Magnus已验证使用Python3.11、torch2.5.1+cu124、tensordict0.6.2及CUDA12.4 devel镜像。旧550驱动不能运行本地torch2.14的CUDA13包；runtime镜像缺编译器会使torch.compile失败。bootstrap负责本地wheel、小依赖和PYTHONPATH；不能直接用根run.sh替代。CPU可见核数可能是宿主机数据，按实际亲和性/配额选线程。

## 与本地 / Vast 环境的差异（踩过的坑）

- **版本栈不同**：Magnus 是 Python 3.11 + torch 2.5.1+cu124 + tensordict 0.6.2（`magnus/bootstrap.sh` 现装），本地与 Vast 是 Python 3.12 + torch 2.14 + tensordict 0.14。两边实验结果不能逐位对比。API 也有差：0.6.2 的 `CudaGraphModule` 没有 `device` 参数，首个 rollout 图 Job `356819cb7a21700f` 因此在 gpucheck 就失败了。**改到 torch / tensordict API 的代码，提交 Job 前先在同版本 CPU venv 里跑相关测试**（torch 2.5.1+cpu、tensordict 0.6.2、`PYTHONPATH=src`）。
- **跨 Job 波动约 6%**：同一份代码在不同 Job 之间，稳态帧率实测相差约 6%（69.1k 对 73.4k）。比较改动时优先在同一 Job 内做 A/B（`graph_probe.sh`、`phase_probe.sh 28 32`），跨 Job 比较时主要看分阶段耗时。

## Job 入口

所有入口先 `source magnus/bootstrap.sh`（校验镜像版本、安装 `magnus/wheels` 与小依赖、设置 `PYTHONPATH=src`），结束时把结果交给 File Custody，secret 写进 Job Result。

| 入口 | 用途 | 结果 |
|---|---|---|
| `bash magnus/smoke.sh` | 环境冒烟：`gpucheck` + 两次 PPO 更新 | 训练结果包 |
| `bash magnus/train.sh <配置> <运行名> [训练器参数]` | 正式单次训练；参数原样传给 `stgtrain.train`（`--total-updates N`、`--resume RUN_DIR`；`--runs-dir` 由脚本固定为 `runs/job-<JobID>`） | `job-<JobID>.tar.gz` |
| `bash magnus/train-multi.sh 配置:名字[:种子] … [-- 训练器参数]` | 同一张卡并跑 K 条训练；每条 env 线程 = (亲和性核数 − 2K) / K（`THREADS=` 可覆盖），配置副本写进结果目录 | `multi-<JobID>.tar.gz`（所有 run 一个包） |
| `bash magnus/bench.sh [配置] [名字]` | `threads × num_envs` 吞吐扫描（`stgtrain.train --bench`） | `bench.json` |
| `[GPUCHECK=1] bash magnus/archive/phase_probe.sh [线程数 …]` | 分阶段计时：每个线程数各跑 20 次更新，每 5 次采一次同步计时，汇总稳态帧率、各阶段中位秒数与每步计数；`GPUCHECK=1` 时先跑 gpucheck | `summary.json` + 各 run |
| `bash magnus/archive/graph_probe.sh` | rollout CUDA 图开 / 关 A/B（先跑 gpucheck） | `summary.json` + 各 run |
| `[KS="1 2 3 4"] [CONFIG=…] [UPDATES=20] bash magnus/archive/parallel_probe.sh` | 同卡并跑 K 条的吞吐扫描（线程按 `train-multi.sh` 的同一公式分），记每条 / 合计稳态帧率与显存峰值；默认配置 `exp-m0-rebase.toml` | `summary.json` + 各 run |

**退出时尝试交回结果**：`train.sh` / `train-multi.sh` / `parallel_probe.sh` 都装了 `trap EXIT`，正常结束、训练失败、
Magnus 发 SIGTERM（终止 / 超时）三种情形都会尝试把已有的 run 目录（含 checkpoint）打包交给 File Custody；
收到 SIGTERM 时先停训练、尝试写好 Result 再以 0 退出，Job 可能记为 Success，仍须检查实际训练与结果包。任一条训练失败时以非零码退出。
共用函数在 `magnus/lib.sh`。

**⚠ 手动 kill 救不回来**（2026-09-25，M0 Job `f58d88682d4b428d` 被用户终止）：Magnus 终止时**先清掉工作区**，训练进程还活着，
接着写 tensorboard 报 `FileNotFoundError` 退出；退出 trap 去打包时 run 目录已不存在，什么都没上传。兜底只对「训练自己失败」
与「超时 SIGTERM 且工作区还在」有效。要在终止前留住结果，得先让训练自己停（例如 `run.max_minutes`），或以后加「中途定期上传」。
评测数字仍在 Job 日志里（`magnus job logs`），可以解析出来。另：Job 实际跑在 zhustation 本机（tfevents 文件名里的主机名）。（2026-09-25 本机 CPU 用 smoke 配置验过三种情形，上传换成桩。）

## 提交与取回

用已推送的固定 commit SHA，分支为 `main`。**优先级一律 `B2`（站点默认；用户 09-25 定，共享集群不抢 A2）**。下例的 32 核、64 GB 来自 2026-09 的测量，核数和内存须按当前空闲量与任务需要调整：

```bash
magnus job submit \
  --task-name stg-rl-train-<名字> \
  --namespace Renko6626 --repo-name stg-rl-train \
  --branch main --commit-sha <已推送的完整 SHA> \
  --gpu-type a100 --gpu-count 1 --cpu-count 32 --memory-demand 64G \
  --ephemeral-storage 20G --job-type B2 \
  --container-image docker://pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel \
  --entry-command 'bash magnus/train.sh configs/base.toml <运行名>'
```

Job 完成后先用 `magnus job status <ID>` 取得 Result 中的 File Custody secret，再用 `magnus receive <SECRET> --output <本地结果包.tar.gz>` 取回。secret 有效期 240 分钟。

`--resume` 指向的 run 目录必须在 Job 启动前已放进 Job 可见的持久挂载路径；目前尚未确认本站给该账号提供的挂载点。

## 旧 CPU 栈检查

涉及 PPO、CUDA 图或 torch／tensordict API 的修改，提交 Magnus 前先在对应旧 CPU 栈运行受影响的已有测试。首次准备示例（`<检查目录>` 自行替换；不要复用旧会话的临时绝对路径）：

```bash
uv venv -p 3.11 <检查目录>/v062
uv pip install --python <检查目录>/v062/bin/python \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  'torch==2.5.1+cpu' 'tensordict==0.6.2' 'numpy<2.3' \
  pytest matplotlib psutil nvidia-ml-py tensorboard magnus/wheels/*.whl
PYTHONPATH=src <检查目录>/v062/bin/python -m pytest -q tests/test_ppo.py
```

最后一行按实际改动选择相关测试。CPU 通过不能替代 CUDA 图在实际 GPU 的验证。

## 项目自有 wheel

本地 `pyproject.toml` 的 `tool.uv.sources` 与 Magnus bootstrap 共用 `magnus/wheels/`。升级时同步 `pyproject.toml`、`uv.lock`、wheel 与 `SHA256SUMS`，核对两端字节一致；构建快照可以基于已核对的源码和补丁，不要求先发布上游 Release。

### 当前版本与来源（2026-11-25）

- `stg_rl` 为 **0.4.11／ENGINE_VER39**，从 stg-engine main `df6676f` 加本地工作区修改，以 `maturin build --release --locked --compatibility manylinux_2_34` 构建。wheel 的 `build_info().git_sha` 为 `df6676f-dirty`。
- 新版可在编译卡时绑定射击资源。经典训练机体的可选平行直射弹在首次有效命中后消失；内建表仍走原来的贯穿结算。ENGINE_VER37 加入首次命中消耗，38 把敌人强制无敌纳入每局碰撞规则、存档与引擎回放。训练配置的选择方法见[配置说明](../configs/README.md)。xform 段池仍为 **2048**；已撤回的 0.4.8／ENGINE_VER36 曾使用 4096 段。
- 0.4.11 修正活动血条的大血量溢出，真实 HP、伤害与 ECL 血线沿用整数。TH06 一面道中首波和 TH18 四面末符各 420 帧、18 项 wheel 缓冲与 0.4.10 逐帧一致。三段标准场景的本机新旧 release 和新版 debug 校验和一致。
- 0.4.10 与 0.4.9 本地对拍：未指定无敌开关时，TH06 一面道中第一波和 TH18 一面首符各 2 个环境、420 帧、18 项缓冲逐帧相同。
- 0.4.9 与 0.4.7／ENGINE_VER35 对拍：使用默认表，TH06 一面道中第一波和 TH18 一面首符各 2 个环境、320 帧、18 项缓冲逐帧相同。新表在 Python 环境验证了单路与双路命中扣血、发射间隔及前排遮挡。引擎默认三段 golden 与本轮改动前逐字节一致。
- 默认仍为 LEGACY／擦弹开启。0.4.5→0.4.6 的 ENGINE_VER32 修改了擦弹统计，旧版 graze 不能直接作同口径对照；该轮三卡回放其余缓冲一致。校验值只维护在 lock 和 `SHA256SUMS`，不在记忆另抄一份。
- `stgagent` wheel 为 0.1.0，来自 `stg-agent-proto` 的 `v0.1.0`（`6b61fa052640377d640e5a7ecee9641b6ac3df96`）。

早期接入的来源与检查分别见 [0.4.3](practice-cards/reports/stg-rl-043-adoption.json)、[0.4.4](practice-cards/reports/stg-rl-044-adoption.json)、[0.4.5](practice-cards/reports/stg-rl-045-adoption.json)；更早实验保留当时版本，不因升级改写其结果。

## 续训与结果保留

续训目录必须先放到 Job 可见的位置；本页尚未登记可直接复用的本站持久挂载路径，实际使用前核验。File Custody 是结果取回渠道，不能作为唯一长期存储；手动终止的工作区丢失风险见上文。迁移初期的锁定环境、专用镜像等建议不再列为当前自动执行待办，研究顺序以[下一步](next-steps.md)为准。

Magnus 参考：`/data/sunyunbo/magnus-docs/official/docs/internals/job-runtime.zh-CN.md` 与 `.../uv-image.zh-CN.md`。
