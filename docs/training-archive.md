# 训练阶段归档

2026-11-13，按用户确认，将全量预训练之前的旧记录、配置、专用脚本和本地产物按阶段归档。内容保留，调整位置及引用；当前模型、近期诊断、临时卡池和Vast测速资料继续放在原位置。

## 入口

| 用途 | 位置 |
| --- | --- |
| 当前研究待办与架构候选 | [研究待办](next-steps.md)：大注意力／时间相关性，待定方案 |
| 历史编码器研究 | [P1–P3计划](superpowers/plans/2026-10-08-density-ablation-perceiver.md)、[P2结果](practice-cards/2026-10-10-density-p2-u2000-results.md)：P1／P2已完成，P3未训练 |
| 当前阶段选择与参考权重 | [当前实验记录](experiments.md) |
| 本轮三机性能与费用 | [当前性能基线](perf-baseline.md) |
| 旧实验登记簿 | [2026-11-13之前的记录](archive/experiments-before-2026-11-13.md) |
| 旧性能优化过程 | [历史性能记录](archive/perf-baseline-before-2026-11-13.md) |
| 当前配置与历史配置 | [配置说明](../configs/README.md)、[历史配置](../configs/archive/README.md) |
| 通用训练与诊断脚本 | [脚本说明](../scripts/README.md) |
| Magnus备用入口 | [Magnus说明](../magnus/README.md) |

`run.sh` 继续负责依赖与训练器入口；`scripts/run-exp.sh` 额外选择线程并保存配置副本／控制台日志；`tools/vast_profile.sh` 用于同包短性能测试。保持现有模型、PPO、引擎和依赖路线，`magnus/wheels` 位置不变。全量预训练的后续决定见[当前实验记录](experiments.md)：用户已确认从零4000次更新，使用新配置exp-full-pretrain.toml；本页归档范围保持。

## 旧路径映射

| 原位置 | 归档位置 | 本次项目数 |
| --- | --- | ---: |
| 旧 `runs/<名称>` | `runs/archive/2026-11-before-full-pretrain/<名称>` | 142 |
| 旧 `dist/<名称>` | `dist/archive/2026-11-before-full-pretrain/<名称>` | 52 |
| 历史 `configs/<名称>.toml` | `configs/archive/<名称>.toml` | 39 |
| Magnus实验专用脚本 | `magnus/archive/<名称>.sh` | 8 |
| `scripts/run-night.sh` | [历史夜间队列](../scripts/archive/run-night.sh) | 1 |

项目数按顶层文件／目录计，包含结果目录及其已有打包副本。逐项映射保存在本机 `runs/archive-maintenance-20261113/manifest.json` 和 `runs/archive/2026-11-before-full-pretrain/MANIFEST.json`。`runs`、`dist` 仍被Git忽略；原始日志、checkpoint配置及结果包里的当时路径保持原样，定位时按上表或清单转换。追溯文档与现有工具的引用已更新。

归档在 `runs` 内的临时分析脚本也保留原文，其中可能硬编码旧路径。历史文档中的复算命令供追溯；复算前复制脚本、按映射调整其输入路径并指定新的输出目录，避免覆盖归档结果。

## 保留在当前区域的产物

- 四组参考训练结果：发布模型B/Shift K8、轻请求A臂、P2 CNN u2000、P2无CNN u2000。具体目录见[当前实验记录](experiments.md#保留的模型参考)。这些参考不代表选定正式预训练初始化。
- `runs/modern-drafts` 临时卡池及其相对链接目标；近期TH15／TH16评测与诊断。
- `runs/vast-profile-20261113`、`runs/vast-market-20261113`：本轮原始性能结果、重算资料及便携测试包。
- `dist` 中当前B/Shift K8 ONNX、TH06NC 20261028系列包与记录、TH18 r5包、TH16追敌草稿包。

Perceiver的历史配置与启动脚本归档，原型源码保持原位且继续暂停；没有训练结果，不恢复执行。原作生产资料、转写稿、卡牌启用状态及独立审核状态不因归档改变。
