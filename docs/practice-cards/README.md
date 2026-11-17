# 评测与合成卡结果

当前方案见[下一步](../next-steps.md)，各轮结果与比较口径统一见[实验记录](../experiments.md)。本目录只保留仍需独立回查的证据。

| 内容 | 入口 |
| --- | --- |
| 639段四组评测共同弱项 | [分析](2026-11-17-shared-weakness-analysis.md)，原始评测和639个GIF位于runs/research/2026-11-16-full-card-comparison/ |
| 单层u4000五作基线 | [基线表](2026-11-14-u4000-multigame-baseline.md)，639段、16070局，各作样本量和时限分别解释 |
| 表示、覆盖、难度与真实碰撞诊断 | [诊断](2026-11-14-u4000-encoder-diagnosis.md)，包括u6000及SA2后续核查 |
| 旧激光结构实验 | [T5–T8](2026-10-02-laser-stage-summary.md)，14维激光token、联合注意力与K差异 |
| 旧CNN消融 | [P2结果](2026-10-10-density-p2-u2000-results.md)，不恢复旧Perceiver任务 |
| 合成激光卡最终验收 | [结果与独立审核摘要](2026-10-01-batch3-results.md)，30张变体和20张专项，3张专项仍禁用 |
| 机器证据与聚合结果 | reports/中的JSON/CSV保留；历史文件名和路径按当时阶段理解 |

游戏侧关键修复保留[子弹链首节点](2026-10-22-th18-bullet-head-fix.md)、[致死子弹漏采](2026-10-22-th18-hazard-fix.md)、[几何审计](2026-10-22-th18-geometry-audit.md)、[2048容量](2026-10-22-capacity2048.md)及[追敌](2026-10-22-enemy-follow.md)。发布模型与研究模型分开，当前包见[TH06NC](2026-10-28-th06nc-clean-package.md)及[TH18工具说明](../../tools/th18-portable/README.md)。

成品与启用状态见[卡库](../../cards/README.md)，新生产任务见[转写总览](../../transcribe/README.md)。试测、机器检查、独立审核和正式收卡分别记录，不因文档合并提升状态。
