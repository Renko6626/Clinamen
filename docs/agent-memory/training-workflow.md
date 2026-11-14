# 租机与 Magnus 启动概况

这里只记入口和结果流向。实际参数以脚本、配置和当前资源为准；提交、推送、启动训练及终止任务分别按用户授权执行。资源与版本同步约定集中在 [AGENTS.md](../../AGENTS.md)。

## 当前阶段的训练环境选择（2026-11-13）

用户要求记录本阶段选择，作为扩大卡池后正式训练的环境起点：

- 平台采用Vast.ai，优先单张RTX5090（32GB显存）、约48vCPU档；同类实例下单时重新核对价格、CPU型号及cgroup实际配额。本次48vCPU实际约46.08核时间，小时价含50GB磁盘约$0.694，均为当次实测。
- 起始运行参数为 `env.num_envs=4096`、`env.threads=30`、`ppo.num_steps=64`、`ppo.amp="bf16"`。4096环境已验证可跑，未做环境数量扫描，不能记成全局最优；30线程是本次该实例的扫描最佳点。
- 软件沿用Python3.12、uv.lock中的torch2.14.0／tensordict0.14.2、stg_rl0.4.7／ENGINE_VER35，CUDA13.0.2 devel Ubuntu24.04镜像需补python3.12-dev。模型保持 `danger_topk_v8`＋`set_attn_v3`＋CNN、64子弹token、8激光token、1层联合自注意力。
- 临时数据口径为686张启用材料、668张实际训练卡。同日晚用户确认从零预训练4000次更新（约10.49亿帧），初始学习率3e-4；沿用现有奖励、运动层、课程与评测划分，不自动延长训练。实际配置和本次实例见[当前实验记录](../experiments.md)，旧权重短测不作为收敛保证。

性能依据见[当前性能基线](../perf-baseline.md)。同等吞吐的4090若低于约$0.412/小时，费用可能更低；保留按实测吞吐和实际报价选择的空间。

## 租机／本地

2026-11-14 21:36北京时间，用户在选定SA2＋64弹、完成最终配置检查并确认充值后，明确要求在Vast启动。从零4000更新已在原5090实例60494618开始，实际46.08核，4096环境／30线程／bf16；新运行独立保存在`/root/stg-full-pretrain/sa2-full-pretrain-20261114/`，本地控制与监控为`runs/sa2-full-pretrain-20261114/`。本轮按$4控制，预计约4.3小时／$3.5–3.6；完成或异常退出后取回结果并停止GPU，保留磁盘。本轮已于11月15日约01:51完成，训练／固定评测4:12:19、累计约$3.55，结果和u4000权重已取回；API核验actual_status=exited，磁盘继续保留。初始化／完成核验及实际运行状态以[实验记录](../experiments.md#sa264弹从零4000更新2026-11-15已完成)和实时核验为准，不复用旧续训的完成状态。

2026-11-14用户另行明确批准从u4000追加2000次到u6000，新增费用上限$1.8，沿用现有结构与卡池；原4000步授权已完成，新阶段及运行状态以[实验记录](../experiments.md#u4000继续训练到u60002026-11-14已启动)和`runs/full-pretrain-resume-20261114/`为准。现有resume恢复权重／Adam／全局计数，但课程统计与环境重建；学习率随总终点6000重新计算，不能当作无缝采样续接或新架构实验。

复制checkpoint到新目录再`--resume`时，必须先按`make_run_dir`建立`checkpoints/`、`eval/`、`plots/`并检查可写。resume入口沿用已有运行目录，不替新目录补齐这些子目录；2026-11-14首次续训因漏建eval，在u4250评测写盘失败，监控取回日志并停机，latest仍为u4000。修正后用独立retry1目录重启，失败费用计入原$1.8总预算，不能重置账户支出基准。

本轮u6000已于2026-11-14完成，权重／结果已取回，16:54北京时间API核验GPU实例exited、磁盘保留；截至该次查询累计新增约$1.577，含首次失败和保留磁盘费用，低于$1.8。最终结果与8卡比较见[编码器诊断跟进](../practice-cards/2026-11-14-u4000-encoder-diagnosis.md#u6000完成结果)及[实验记录](../experiments.md)，不自动继续训练或把磁盘保留视为销毁授权。

```bash
bash run.sh configs/base.toml my-run
bash run.sh --resume runs/<运行目录>
```

`run.sh` 负责锁定依赖、训练、评测、出图和打包，结果留在 `runs/`。新机器可先用 `bash run.sh configs/base.toml --bench` 选吞吐参数，或用 `bash run.sh --probe` 做租机巡检；这两个入口仍会执行实际计算。

`base.toml` 是TH06示例；本轮全卡池配置为 `configs/exp-full-pretrain.toml`，本机使用modern-drafts临时目录，便携包把卡解引用到单一cards目录。[当前配置](../../configs/README.md)与[脚本入口](../../scripts/README.md)列出仍在使用的入口；`scripts/run-exp.sh` 按显式 `--threads`、配置 `env.threads`、bench的顺序选线程，保存实际配置副本。历史配置、实验专用脚本和旧结果见[阶段归档](../training-archive.md)，不作为默认开跑队列。

开跑前确认 cgroup 实际 CPU 配额与 GPU，再决定并行数和每条线程数；不要沿用旧租机的核数。后台启动后检查真实训练进程和日志，完成后取回结果包。入口详见 [README](../../README.md)。

### Vast.ai 本地凭据

2026-11-13 用户决定接下来一段时间使用 Vast.ai 训练，并要求从 bloodSimulator 复制相关配置。本仓根目录 `.env` 保存 `VAST_API_KEY`、`VAST_API_BASE_URL` 和 `VAST_SSH_KEY_PATH`；文件被 Git 忽略，权限为 `0600`，不随仓库分发。密钥来源为同机 bloodSimulator 的 `.env`，SSH 使用已有 `/data/sunyunbo/.ssh/blood-vast-ed25519`，不复制私钥。

读取本地配置后可通过官方 REST API 操作：基础地址为 `https://console.vast.ai`，在内存中设置 `Authorization: Bearer <VAST_API_KEY>` 请求头；`GET /api/v0/users/current` 查看账户，`GET /api/v1/instances` 查看实例。不要输出密钥、整份 `.env` 或可能带令牌的原始响应。

同日按用户要求用pip安装官方 `vastai` CLI 1.11.0，位于项目外的独立工具环境 `/data/sunyunbo/.local/share/vastai-cli/`，入口 `/data/sunyunbo/.local/bin/vastai` 已在PATH。直接执行 `vastai show instances`、`vastai show user`；使用与本项目相同的key，凭据文件为 `/data/sunyunbo/.config/vastai/vast_api_key`，权限0600。独立环境 `pip check` 通过，两项CLI只读查询成功。最初用户级安装引起的共享依赖覆盖已撤销，原有Miniconda依赖版本恢复；不把CLI依赖加入本项目pyproject或uv.lock。

同日三机短测已完成，详见[性能记录](../perf-baseline.md)文末：当前686张混合卡池、668训练卡、v8/v3＋CNN，5090/48vCPU约106k帧/s、4090/32约63k、4090/64约55k；正式预训练的父权重与预算仍未确定。便携包在 `runs/vast-profile-20261113/final/stg-vast-profile.tar.gz`，入口 `tools/vast_profile.sh`，已补齐镜像缺失的python3.12-dev。实例60478102／60478103／60478104均在取回结果后销毁，最后实例列表为空；此事实不授权再租机或开始长训。console入口不稳定时可给CLI加 `--url https://cloud.vast.ai`；非交互销毁须加 `--yes`。三机原始结果与重算脚本在 `runs/vast-profile-20261113/`。

租机型号、预算、训练参数和开跑另按用户安排决定；旧 bloodSimulator 实例不作为本项目默认训练目标。实际连接时从 API 重新取得实例 ID、SSH 地址及端口。停止实例会保留磁盘并可能继续产生存储费；销毁会删除实例数据，不能将停止授权视作销毁授权。

同日按用户明确确认，已销毁旧 RTX 3060 实例 `58212504`、`58263433` 及其磁盘；两次 DELETE 均返回 HTTP 200、`success=true`，随后实例列表为空。迁入的本地 key 已通过账户及实例 GET 查询，SSH 私钥与账户已登记公钥匹配；本次未租机或启动训练。

### 临时纳入现代作工作稿

2026-11-13用户允许临时启用TH14／TH15／TH16／TH18待验收稿，已有明确禁用／暂缓决定仍保留。本地临时卡池在被忽略的 `runs/modern-drafts/`，`data.toml` 是数据选择覆盖项，需合并到后续选定的实验配置；它不代表模型、轮数或租机预算已确定。链接467张当前启用工作稿，与正式库合并共686张；沿用 `eval/splits-laser.toml` 和合成留出规则后，实际训练668张。加载器选卡、起点构造及禁用项排除检查通过，尚未整批编译、运行验收或启动训练，作者／审核状态不提升。

4张TH16 Extra稿（s7_b4、s7_b15、s7_b18、s7_mb3）的 `ranks=[4]` 不符合现有加载器闭区间格式，仅在临时卡池复制并改为等价的 `[4,4]`；源稿和ECL不变。其余仍为相对符号链接，向租机传输时须携带目标或解引用复制。临时目录可再生成，不作为正式收卡位置。

## Magnus

1. 用 `magnus cluster` 查空闲资源；提交已获授权、已推送的固定 commit，显式使用 B2。
2. Job 入口通常为 `bash magnus/train.sh <配置> <运行名>`；同卡多条用 `magnus/train-multi.sh`，首次环境核验用 `magnus/smoke.sh`。
3. `magnus/bootstrap.sh` 安装仓内 wheel 和指定依赖，随后训练／评测；退出时尝试打包并交给 File Custody。
4. 提交几分钟后查状态，结束后从 Job Result 取 secret，用 `magnus receive <SECRET> --output <结果包>` 下载。历史协议记录有效期为 240 分钟，收到结果后及时取回；实际期限以服务返回为准。

Magnus 入口使用 Python 3.11、torch 2.5.1+cu124、tensordict 0.6.2；本地按 `uv.lock` 安装，不能直接在 Magnus 镜像运行根目录 `run.sh` 替代 bootstrap。需要编译器的路径使用 CUDA 12.4 **devel** 镜像。修改 PPO／相关 API 后先做对应旧 CPU 栈检查，CUDA 图再在真实 GPU 核验。

脚本会尝试交回已有结果，但手动终止可能先删除工作区，不能保证救回 checkpoint；需要保留时先让训练按计划自行停止并取回结果。具体提交参数、旧 CPU 栈准备和 wheel 来源见 [Magnus 说明](../magnus-migration.md)。
