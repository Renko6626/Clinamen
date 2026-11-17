# stg-rl-train

stg-engine弹幕环境的PPO训练、评测和ONNX导出仓库，也保存TH06／TH14／TH15／TH16／TH18转写资料和合成练习卡。

2026-11-17：无位置任务MQ4已完成u4000，现代16卡同GPU原MQ4 34.57%→38.77%。下一阶段已确认[逐弹全局场景token替换CNN](docs/superpowers/specs/2026-11-17-mq4-global-latents-design.md)，尚未实现或开训，512／1024输入与运行预算待成本短测后决定。研究顺序见[下一步](docs/next-steps.md)，结果和比较限制见[实验记录](docs/experiments.md)。研究模型不自动替换发布模型。

| 用途 | 入口 |
| --- | --- |
| 当前模型、评测与成本 | [实验记录](docs/experiments.md)、[性能记录](docs/perf-baseline.md)、[证据专题](docs/practice-cards/README.md) |
| 训练与复现 | [配置](configs/README.md)、[脚本](scripts/README.md)、[启动概况](docs/agent-memory/training-workflow.md)、[Magnus兼容](docs/magnus-migration.md) |
| 卡库与生产 | [卡库](cards/README.md)、[转写流程](transcribe/README.md)、各作指南；TH14／TH15阶段结束，搁置和排除卡不恢复 |
| 历史权重、结果包与路径 | [产物索引](docs/training-archive.md) |

## 训练实现

src/stgtrain/envwrap.py将stg_rl原始缓冲解码为观测并处理运动层；featurize/与models/负责表示和网络，ppo.py负责优化，train.py编排采样、评测、checkpoint和课程。各组件通过registry/config配置选择；代码中的模型、特征化器和图签名按各自版本解释，旧初始设计不再作当前接口规范。

实际弹幕、碰撞、实体池与ECL编译在相邻stg-engine；游戏快照与共用C推理在stg-agent-proto，原生研究与游戏适配在renkolab。模型接口使用固定形状Mapping输入，输出18方向/低速动作logits与value；跨仓接口或引擎变化按AGENTS约定确认和验证。

当前依赖以pyproject.toml、uv.lock和magnus/wheels为准；stg_rl 0.4.7／ENGINE_VER35的[来源与兼容边界](docs/magnus-migration.md#项目自有-wheel)包括2048段池、xform标签及屏外保活，不恢复已撤销的临时扩池版本。

## 一条命令跑训练（任意有 GPU 的 Linux）

```bash
git clone https://github.com/Renko6626/stg-rl-train && cd stg-rl-train
bash run.sh configs/base.toml my-run          # 装依赖 → 训练 → 评测 → 出图 → runs/<时间>-my-run.tar.gz
bash run.sh --resume runs/<目录>               # 续训
bash run.sh configs/base.toml --bench          # 新机器先测吞吐，选 threads × num_envs
```

`base.toml` 是TH06通用示例，不是本轮扩大卡池的正式预训练方案。环境模拟在CPU上运行；本次5090短测PPO更新约占61%，环境步约占11%。租机需核对CPU型号、cgroup实际配额并实测吞吐，不能只按核心数选型。

## 探测模式：新机器先跑这个

测安装可达性（uv / PyPI / GitHub）与 CPU / GPU 负载，约 20 分钟，产出**一个**结果包：

```bash
git clone https://github.com/Renko6626/stg-rl-train && cd stg-rl-train
bash run.sh --probe                    # 可选 --minutes 60
# → runs/probe-<主机名>-<时间>.tar.gz，把这个文件发回来
```

顺序：网络探测（各域名连通 + torch wheel 下载测速）→ 计时安装 → 系统信息（lscpu / nvidia-smi …）→
gpucheck（有 CUDA 才跑）→ bench 选 num_envs / threads → 用 `probe/cards` 的 7 张卡限时训练。
每步失败都记下来继续，照样打包。包里 `SUMMARY.md` 是汇总，`train/plots/load.png` 是负载曲线，
`train/perf.jsonl` 是每秒一行的原始负载数据。

## 导出部署用的 ONNX 图

把一个 checkpoint 导成**特征化 + 网络合体**的单文件定形图，给 th06nc / TH18 的 DLL 用
（ORT CPU 跑）。特征化也进图，所以 C 侧不必复刻 topk / 密度图 / 归一化 —— 逐位一致由
「两边是同一张图」保证。设计见 renkolab `docs/superpowers/specs/2026-09-18-th06nc-onnx-policy-design.md`。

```bash
uv run --frozen python -m stgtrain.export_onnx runs/<run>/checkpoints/best.pt --out dist --name j-best
# → dist/j-best.onnx（约 1.4 MB，权重内联，单文件）+ dist/j-best.manifest.json（出处与图签名）
```

导出后会自动拿 onnxruntime 与 torch 对一遍 logits（偏差 > 1e-5 或 argmax 不同就退非零码）。
支持 `danger_topk_v2` / `danger_topk_v3`，两者导出的都是**图版本 2** 的同一套签名（`enemies` 六列，
后两列是敌人速度；v2 的图不读它们），所以同一个 DLL 能换着装。敌人速度不在图里：训练侧自
`stg_rl` 0.2.0 起直接读引擎 Tier 0 的 `vx`/`vy` 字段（本帧实际位移，瞬移不计入）；C 端 `sa_model_fill`
仍按 id 跨帧差分自己填（含 16 px 瞬移守卫），两边口径暂不一致，图是无状态的、不要求逐位相同。
再换特征化器要在 `EXPORT_FEATURIZERS` 加一个可导出孪生；动了图签名还要两边一起 bump `GRAPH_VERSION`。`dist/` 不入库，按 `rl-vX` wheel 的先例走 Release 分发。

当前激光模型路线由T6–T8验证，统一[阶段小结与后续候选](docs/practice-cards/2026-10-02-laser-stage-summary.md)：`danger_topk_v8` 使用14维激光token（局部线段几何、有限旋转位移、伸长余量、预警），`set_attn_v3` 将子弹和激光分别投影后送入一层共享自注意力，再按类型池化。它替换旧子弹专用注意力层；主干、PPO与T5训练设置沿用。[设计与字段契约](docs/superpowers/specs/2026-10-01-laser-token-joint-attention-design.md)。

v8的640行导出为**图版本6**：在版本5的激光表／mask之后追加 `laser_start_len: float32[L]`，必须与激光行对齐，填引擎的设定棒长，不能用当前长度代替。当前部署默认2048行，为**图版本7**，十二输入名称和列序沿用；旧640行可显式传 `--bullets-rows 640`。版本2–6旧签名继续由新C loader兼容。T8历史TH06NC包见[记录](docs/practice-cards/2026-10-02-laser-stage-summary.md#工程交付)，当前2048部署见下节。

## TH06NC 精简发布包

当前本地包为 `dist/th06nc-ai-20261028.zip`（6 个文件，6.27 MB），只带最新 B/Shift K8 graph7 模型、x64 插件、ONNX Runtime、简短配置、使用说明与许可证。关闭游戏后备份同名文件，将包内文件复制到 `th06nc.exe` 旁；默认手动，C 切换模式。沿用系统 VC++ x64 运行库要求，尚未完成本版 Windows 游戏内验收，也未上传公开 Release。[打包入口与交付记录](docs/practice-cards/2026-10-28-th06nc-clean-package.md)。

## TH18 自包含启动包

当前使用 `dist/th18-ai-probe-20261022-r5.zip`：世界快照与ONNX原始弹表均为2048行，适配层不排序，只保留图内TopK。同一checkpoint重导出为graph7，无需重训；保留激光状态、解冻首帧、子弹入口修复和Boss优先追敌。此前的 `th18-ai-portable-20261022-r2.zip` 仅修正启动配置路径，仍含子弹读取错误。容量升级与验证见[记录](docs/practice-cards/2026-10-22-capacity2048.md)，漏采修复经过见[记录](docs/practice-cards/2026-10-22-th18-hazard-fix.md)。

随包提供现有 thcrap x86、AI 插件、模型和所需的非系统运行库，游戏文件须自行准备。完整解压到可写的短目录（如 `D:\TH18-AI`），双击 `TH18-AI.exe`，首次选择 TH18 v1.00a 原版游戏程序，之后直接双击启动。

默认 MANUAL，F10 切换 MANUAL／AUTO／BYPASS，C／D／X 保持手动，自动炸弹关闭。推荐 Windows 10 22H2／Windows 11；未做 Windows 游戏实机验收。构建、校验、路径限制与使用说明见 [打包工具文档](tools/th18-portable/README.md)。

## 卡库与生产入口

成品按 `cards/<th06|th16|th18|synthetic>/` 归档，生产资料对应 `transcribe/` 下同名目录；TH16当前仍是工作区候选，未收进正式卡库。题材与启用状态使用metadata，训练配置明确选择来源与标签。见[卡库说明](cards/README.md)和[生产总览](transcribe/README.md)。

## 开发

```bash
uv sync --frozen
uv run --frozen pytest -q
bash run.sh configs/smoke.toml smoke           # CPU 冒烟
uv run --frozen python -m stgtrain.plots runs/<目录>   # 重画曲线
```
