# 训练配置

当前保留以下训练与性能短测配置，运行路径相对仓库根目录解析。

| 配置 | 用途 |
| --- | --- |
| [base.toml](base.toml) | TH06通用训练示例；不是本轮全卡池预训练方案 |
| [smoke.toml](smoke.toml) | 测试夹具上的轻量CPU冒烟 |
| [probe.toml](probe.toml) | 新机器巡检负载，由 `run.sh --probe` 使用 |
| [exp-full-pretrain.toml](exp-full-pretrain.toml) | 2026-11-13确认：扩大卡池、从零初始化、4000次更新、学习率3e-4 |
| [exp-th16-mq4-u500.toml](exp-th16-mq4-u500.toml) | 2026-11-15用户将TH16-only测试改为u500，已完成并停GPU；110起点、从零MQ4。必须使用[专用入口](../tools/train_th16_probe.py)保留混合训练前500更新的4000退火分母，6张诊断卡留在训练中。见[实验记录](../docs/experiments.md#th16-only-mq4-u500测试2026-11-15) |
| [exp-full-pretrain-mq4-free.toml](exp-full-pretrain-mq4-free.toml) | 2026-11-17用户授权无位置任务实验：原MQ4从零4000更新，训练／评测均自由档，跟点塑形与驻点奖励为零；保留原按键／变向／低速切换／贴边惩罚及运动闸。已完整u4000并取回停GPU，现代34.57%→38.77%；见[最终结果](../docs/experiments.md#无位置任务正式完成与同量对照2026-11-17) |
| [exp-full-pretrain-mq4-player.toml](exp-full-pretrain-mq4-player.toml) | 2026-11-16用户授权：保留MQ4，19维自机／条件映射为一个额外token，与64弹＋8激光共同交流并供四查询读取；从零4000更新已完成，结果取回且GPU已停；现代GPU同量34.57%→33.89%，未显示整体收益，其他训练配置不变。见[设计与验证](../docs/experiments.md#mq4加入自机token2026-11-16) |
| [exp-full-pretrain-mq4.toml](exp-full-pretrain-mq4.toml) | 2026-11-15确认结构并完成本地准备：K64单层、4查询统一读取弹／激光、1层摘要交互，替换威胁mean/max/单查询汇总；目标4000更新，现代诊断每500更新；[结构与检查](../docs/superpowers/specs/2026-11-15-multi-query-readout-design.md)。用户随后明确跳过短测，4000更新正式训练已完整完成，结果取回且GPU已停 |
| [exp-full-pretrain-k128.toml](exp-full-pretrain-k128.toml) | 已提前结束的历史配置：原计划4000更新，日志到u2373、最新权重u2250；单层K128、num_minibatches32，现代诊断与旧TH06分开保存；见[本轮负结果](../docs/experiments.md#k128单层扩视野实验2026-11-15提前结束)，不作为待运行任务 |
| [exp-full-pretrain-sa2.toml](exp-full-pretrain-sa2.toml) | 2026-11-14用户选定：两层联合注意力＋64弹，从零4000更新；仅joint_sa_layers从1改为2，CPU及80更新同机GPU短测完成；方案／对照／成本见[SA2评估](../docs/experiments.md#sa264弹从零4000更新2026-11-15已完成)，2026-11-15正式4000更新已完成，结果已取回且GPU已停；见[完成记录](../docs/experiments.md#sa264弹从零4000更新2026-11-15已完成) |
| [exp-request-light-shift-k8.toml](exp-request-light-shift-k8.toml) | 当前发布模型B/Shift K8的历史训练口径 |
| [exp-density-cnn.toml](exp-density-cnn.toml) | P2 CNN候选模型与本轮Vast测速的结构基线 |
| [exp-density-none.toml](exp-density-none.toml) | P2无CNN对照 |

另有性能探针专用[perf-k128.toml](perf-k128.toml)和[perf-k256.toml](perf-k256.toml)：单层、4096环境×64步、num_minibatches=32、30更新，使用`tools/vast_token_profile.py`，不作为正式训练方案。实测与运行命令见[GPU短测](../docs/perf-baseline.md#k128k256单层gpu短测2026-11-15)。

后面三份保留作模型参考，包含当时的卡池、学习率和轮数，不直接代表新一轮训练方案。全量预训练配置已合并本机 `runs/modern-drafts/data.toml`，本地需要该临时目录；上传包使用解引用复制后的单一cards目录，686张材料、668训练卡。只运行旧CNN配置不会使用全部668张训练卡。

K128历史运行入口（现代诊断与旧留出分别保存；本轮已结束，命令仅供复现，不是续训授权）：

```bash
.venv/bin/python tools/train_with_diagnostics.py --diagnostic-splits eval/modern-diagnostic.toml configs/exp-full-pretrain-k128.toml sa1-k128-zero --no-pack
```

MQ4正式训练入口（2026-11-15用户明确跳过短测后已完成；下列为历史入口，不重复启动）：

```bash
.venv/bin/python tools/train_with_diagnostics.py --diagnostic-splits eval/modern-diagnostic.toml configs/exp-full-pretrain-mq4.toml mq4-zero --no-pack
```

MQ4保持原训练留出划分，现代16卡仍在训练中；不把modern-diagnostic.toml填入env.eval_splits。不使用旧v3 checkpoint续训或迁移权重。

本阶段环境起点为5090／约48vCPU、4096环境、30线程、64步、bf16，4096不是已验证的最优值；见[性能基线](../docs/perf-baseline.md)。线程可用 `scripts/run-exp.sh <配置> <名称> --threads N` 显式覆盖。

其余39份历史研究配置已移至[archive](archive/README.md)，用途及结论见[旧实验记录](../docs/experiments.md#历史实验)。
