# 训练配置

当前保留以下八个配置，运行路径相对仓库根目录解析。

| 配置 | 用途 |
| --- | --- |
| [base.toml](base.toml) | TH06通用训练示例；不是本轮全卡池预训练方案 |
| [smoke.toml](smoke.toml) | 测试夹具上的轻量CPU冒烟 |
| [probe.toml](probe.toml) | 新机器巡检负载，由 `run.sh --probe` 使用 |
| [exp-full-pretrain.toml](exp-full-pretrain.toml) | 2026-11-13确认：扩大卡池、从零初始化、4000次更新、学习率3e-4 |
| [exp-full-pretrain-sa2.toml](exp-full-pretrain-sa2.toml) | 2026-11-14用户选定：两层联合注意力＋64弹，从零4000更新；仅joint_sa_layers从1改为2，CPU及80更新同机GPU短测完成；方案／对照／成本见[SA2评估](../docs/next-steps.md#当前小步对照两层联合注意力sa2)，2026-11-15正式4000更新已完成，结果已取回且GPU已停；见[完成记录](../docs/experiments.md#sa264弹从零4000更新2026-11-15已完成) |
| [exp-request-light-shift-k8.toml](exp-request-light-shift-k8.toml) | 当前发布模型B/Shift K8的历史训练口径 |
| [exp-density-cnn.toml](exp-density-cnn.toml) | P2 CNN候选模型与本轮Vast测速的结构基线 |
| [exp-density-none.toml](exp-density-none.toml) | P2无CNN对照 |

后面三份保留作模型参考，包含当时的卡池、学习率和轮数，不直接代表新一轮训练方案。全量预训练配置已合并本机 `runs/modern-drafts/data.toml`，本地需要该临时目录；上传包使用解引用复制后的单一cards目录，686张材料、668训练卡。只运行旧CNN配置不会使用全部668张训练卡。

本阶段环境起点为5090／约48vCPU、4096环境、30线程、64步、bf16，4096不是已验证的最优值；见[性能基线](../docs/perf-baseline.md)。线程可用 `scripts/run-exp.sh <配置> <名称> --threads N` 显式覆盖。

其余39份历史研究配置已移至[archive](archive/README.md)，用途及结论见[旧实验记录](../docs/archive/experiments-before-2026-11-13.md)。
