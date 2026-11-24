# 训练启动概况

最后核对：2026-11-25（临时卡池统计）。

此页保留可复用操作；具体方案、预算及运行结果见[下一步](../next-steps.md)和[实验记录](../experiments.md)。旧实例号、价格、余额与停止记录不作为当前事实。

## 租机／本地

```bash
bash run.sh configs/base.toml my-run
bash run.sh --resume runs/<运行目录>
```

run.sh负责锁定依赖、训练、评测、出图和打包；base.toml只是TH06示例，当前实验模板见[配置入口](../../configs/README.md)。[脚本入口](../../scripts/README.md)说明线程选择。已授权的新机器测试可用bench／probe，均会实际执行计算。

- 开跑前查CPU cgroup cpu.max/cpu.stat、亲和性和GPU；nproc与逐核占用可能来自宿主机。线程数按当前配额和实测选，不照抄旧30线程或旧实例核数。
- 新环境按uv.lock，CUDA devel镜像须有编译器和Python头文件。实例地址、SSH端口和报价通过平台重新取得。
- 后台启动须核对真实Python、日志和CPU/GPU占用；监控同时处理完成与提前退出。取回产物再停GPU，停止保留磁盘并继续计费，销毁另需授权。
- --resume恢复权重、Adam、RNG与全局计数，但环境和课程重建；扩大总更新终点会重算LR，不等价无缝续训。复制checkpoint到新目录前按make_run_dir补齐checkpoints/eval/plots并检查可写，不能只建checkpoints。
- 自动监控结束后核对实际checkpoint计数、完整日志和评测；平台停止状态或外层shell存活均不能替代训练完成证据。

## 临时现代作卡池

2026-11-25 通过 `configured_cards` 与 `train_starts` 核对，移出 TH15 Extra 第四波后的混合池有 685 张启用卡，依现有留出规则有 667 张可用于训练。11 月 13 日建池时为 686／668；复现当时训练与评测应使用当次材料。临时池链接原作者稿，后续 HP 迁移工作包单独保存，整卡独立审核与正式收卡另计。[TH15 停用项](../../transcribe/th15/README.md) · [迁移进度](../../transcribe/README.md#可击破迁移)

四张 TH16 Extra 的 rank 区间在临时副本中记为 `[4,4]`。传输其他临时稿时须携带相对链接目标，或解引用复制。[本机卡池入口](../../runs/modern-drafts/data.toml)

### Vast.ai 本地凭据

2026-11-13 用户决定接下来一段时间使用 Vast.ai 训练，并要求从 bloodSimulator 复制相关配置。本仓根目录 `.env` 保存 `VAST_API_KEY`、`VAST_API_BASE_URL` 和 `VAST_SSH_KEY_PATH`；文件被 Git 忽略，权限为 `0600`，不随仓库分发。密钥来源为同机 bloodSimulator 的 `.env`，SSH 使用已有 `/data/sunyunbo/.ssh/blood-vast-ed25519`，不复制私钥。

读取本地配置后可通过官方 REST API 操作：基础地址为 `https://console.vast.ai`，在内存中设置 `Authorization: Bearer <VAST_API_KEY>` 请求头；`GET /api/v0/users/current` 查看账户，`GET /api/v1/instances` 查看实例。不要输出密钥、整份 `.env` 或可能带令牌的原始响应。

同日按用户要求用pip安装官方 `vastai` CLI 1.11.0，位于项目外的独立工具环境 `/data/sunyunbo/.local/share/vastai-cli/`，入口 `/data/sunyunbo/.local/bin/vastai` 已在PATH。直接执行 `vastai show instances`、`vastai show user`；使用与本项目相同的key，凭据文件为 `/data/sunyunbo/.config/vastai/vast_api_key`，权限0600。独立环境 `pip check` 通过，两项CLI只读查询成功。最初用户级安装引起的共享依赖覆盖已撤销，原有Miniconda依赖版本恢复；不把CLI依赖加入本项目pyproject或uv.lock。

CLI位于项目外独立工具环境，避免把Vast工具依赖加入本项目。console入口不可用时可尝试CLI的--url https://cloud.vast.ai。非交互销毁参数--yes仅是参数，不代表销毁授权；不把平台凭据、完整.env或带令牌响应输出到日志。

## Magnus

1. magnus cluster查当前空闲CPU/GPU；提交已授权、已推送的固定commit，显式--job-type B2。
2. magnus/train.sh、train-multi.sh负责bootstrap和训练；结束时尝试交File Custody。提交数分钟后查实际状态。
3. 从Job Result取得secret后及时magnus receive下载；历史有效期240分钟，实际以服务返回为准。手动kill可能先删除工作区，不能保证救回checkpoint。

Magnus为Python3.11、torch2.5.1+cu124、tensordict0.6.2，使用CUDA12.4 devel镜像；本地按锁文件。PPO或相关API变化先做[旧CPU栈检查](../magnus-migration.md#旧-cpu-栈检查)，CUDA图另需实际GPU验证。wheel升级同步依赖、锁、magnus/wheels和SHA256SUMS，细节见[Magnus说明](../magnus-migration.md)。
