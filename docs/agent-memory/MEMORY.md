# 项目记忆索引

最后核对：2026-11-25（可击破转写入口）。稳定工作约定见[AGENTS.md](../../AGENTS.md)，本索引仅维护长期背景和当前入口。

- [项目背景](project-context.md)：仓库分工、东方／ECL概念与游戏接入。
- [证据位置](evidence-map.md)：现有Ghidra、原生调查、引擎手册。
- [训练启动概况](training-workflow.md)：通用入口、资源核验、环境兼容和结果取回。
- [模型命名候选](../2026-11-09-model-naming-ideas.md)：用户偏好，尚未定名。

## 当前工作入口

已确认[逐弹全局场景token替换CNN](../superpowers/specs/2026-11-17-mq4-global-latents-design.md)，保留近场MQ4，16维逐弹编码、32×64全局token及两层近远联合计算。用户要求先保存文档、下一阶段实施；512／1024待成本短测选择，优先争取1024。尚未实现或开训，收费短测和训练预算另定。

无位置任务MQ4已完整u4000，同GPU现代16卡34.57%→38.77%，作为后续模板；原MQ4、自机token、SA2、K128及续训均已结束。最后收尾记录两地GPU停止、磁盘保留；资源实际状态执行时重新核验，不恢复旧训练或自动部署。

[下一步](../next-steps.md)维护当前安排；[实验结果](../experiments.md)保存比较协议、结论和限制；[共同弱项分析](../practice-cards/2026-11-17-shared-weakness-analysis.md)与[五作基线](../practice-cards/2026-11-14-u4000-multigame-baseline.md)保留研究证据。原始权重、逐局记录及639个GIF仍在忽略的runs中，定位见[产物索引](../training-archive.md)。

转写从[统一流水线](../../transcribe/README.md)、[可击破转写与实射验收](../../transcribe/contracts/killable.md)及本作指南进入；TH14／TH15阶段收尾和各作排除/搁置决定不因文档清理、机器检查或临时训练许可改变。
