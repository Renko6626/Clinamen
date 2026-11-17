# 实验产物与历史路径索引

更新：2026-11-17。旧计划和过程文档已删减；独立结果收敛在[实验记录](experiments.md)、[性能记录](perf-baseline.md)及各专题。本页只定位仍保留的产物，不作为待执行队列。

## 近期产物

| 内容 | 本机目录 |
| --- | --- |
| 无位置任务MQ4 | runs/mq4-free-experiment-20261117/；接续与最终权重runs/mq4-free-resume-shaanxi-20261117/results/ |
| MQ4自机token | runs/mq4-player-experiment-20261116/results/ |
| MQ4被终止的续训 | runs/mq4-resume-shaanxi-20261116/results/，latest u5250、best u4000 |
| 全639段四组评测与639个GIF | runs/research/2026-11-16-full-card-comparison/，含CSV/JSON、GIF索引及weakness-analysis/ |
| MQ4与旧K64同CPU比较 | runs/mq4-u4000-compare-20261115/ |
| MQ4混合训练／TH16-only | runs/mq4-experiment-20261115/；runs/th16-mq4-probe-20261115/ |
| K128及同量对照 | runs/k128-experiment-20261115/；runs/k64-k128-u2000-compare-20261115/ |
| 单层全卡池u4000／u6000、SA2 | runs/full-pretrain-20261113/；runs/full-pretrain-resume-20261114/；runs/sa2-full-pretrain-20261114/ |
| 临时训练数据 | runs/modern-drafts/及其相对链接目标，不能随清理删除 |
| 性能短测 | runs/vast-profile-20261113/；runs/sa2-short-20261114/；runs/token-profile-20261115/；runs/cpu-architecture-bench-20261114/ |

版本化聚合结果位于docs/practice-cards/reports/；机器JSON、CSV和图像保留。逐局日志、checkpoint、原始回放和结果包位于被忽略的runs，不随本轮文档清理删除。

## 2026-11-13历史路径映射

| 原位置 | 现位置 |
| --- | --- |
| 旧runs顶层的142项 | runs/archive/2026-11-before-full-pretrain/<原名称> |
| 旧dist顶层的52项 | dist/archive/2026-11-before-full-pretrain/<原名称> |
| 39份旧配置 | configs/archive/<原名称>.toml |
| Magnus旧实验脚本 | magnus/archive/<原名称>.sh |
| 旧夜间队列 | scripts/archive/run-night.sh |

逐项映射保留在本机runs/archive-maintenance-20261113/manifest.json及runs/archive/2026-11-before-full-pretrain/MANIFEST.json。日志和包内当时路径不改写；复算旧脚本前按映射调整输入，并使用新输出目录，避免覆盖结果。

四组保留参考权重见[实验记录](experiments.md#保留的模型参考)，未随旧runs迁走。当前包仍留dist顶层：B/Shift K8 graph7、TH06NC 20261028系列、TH18 r5和TH16追敌草稿；训练模型与发布模型分别按checkpoint和manifest核对。工具构建与游戏内实机验收是不同证据。

配置和脚本的现行入口见[configs](../configs/README.md)、[scripts](../scripts/README.md)、[Magnus](../magnus/README.md)。存在历史配置或保留磁盘不代表恢复训练、启用卡或销毁资源的授权。
