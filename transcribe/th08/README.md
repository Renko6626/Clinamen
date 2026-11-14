# TH08 源准备

2026-11-08：已建立 TH08 v1.00d 的源工作区与 renkolab Ghidra 工程，导入本版本 th-re-data。当前完成解包、反编译、索引与资料导航，尚未切分攻击、派发作者或接入训练流水线。

## 下一会话从这里继续

用户在TH15及其评测阶段归档后，指定下一会话处理TH08。本轮仅准备交接，不启动切分或作者。目标仍为合成训练数据，复用现有流水线；需要原生核对时先使用社区re-data已导入的函数名、类型和标签，不跳过命名层裸读，也不把全表逆向设为前置。

1. 先用本页及work索引确认旧式sub、timeline、变量继承和难度标记；按实际原文整理TH08转写规则，避免复制现代作编号及EX数值。
2. 核对24个源文件的实际普通流程、分支路线、练习文件与特殊文件归属，再选短攻击切分；不要按文件数、sub数或练习副本重复计卡，不在尚未定位前预设所有关卡ID。
3. 按攻击闭包整理funcSet/funcCall用途和其他真实缺口；277处是调用数，不是277张卡。TH08停用值仅有社区资料的-1，不能搬TH15的0号含义。
4. 复用现有任务模板、官方headless清单和`transcribe/run.py`。当前来源／卡ID校验尚未接入TH08，弹型合成映射与必要指令配方也待整理；按所选攻击在现有模块内补必要兼容，不另建调度器或先扩引擎。
5. 任务包准备后按下一会话实际指令决定作者批次。历史Qoder dfmodel探测不可用、DSH flash/high曾可用均为2026-11-08观察，届时核验，不自动沿用旧额度判断或退回Auto选模。

TH15的6个搁置项、历史模型A/B再评、训练和编码器改造都不属于本次TH08交接的默认工作。TH15报告与评测入口在[阶段记录](../th15/README.md)，总体研究顺序在[下一步](../../docs/next-steps.md)。

## 本机入口

- [工作区说明](../work/th08/README.md)：24 份 ECL、mapped/raw 文本、复现命令与日志。
- [定义索引](../work/th08/source-context/index.json)：1,449 个 sub、32 个 timeline 的文件及行号；共 52,725 行 mapped 文本。统计包含普通与其他模式文件中的重复定义，不代表攻击数。
- [特殊函数调用](../work/th08/source-context/special-functions.json)：277 处 `funcSet/funcCall`，保留文件、sub、行号和参数；未逐项判定用途。
- renkolab 登记：`games/th08.v1.00d/INDEX.md`；工程：`local/th08.v1.00d/ghidra_projects/th08.exe.gpr`；离线资料：`local/th08.v1.00d/state/index.html`、`state/data/functions.jsonl`。需要补读原生时复用此工程，不重新建库。

EXE 版本串为 `Imperishable Night. ver 1.00d`。原始 exe/dat 从相邻 th18-leveledit 的 `local/th08-origin-game/` 复制到 renkolab 的 `local/th08.v1.00d/`，原目录保持不动；转写工作区另存 dat。

工程已导出 2,383 个函数页；社区导入包含 123 个游戏结构体、553 个 opcode 标签和 189 个全局类型绑定。类型阶段有 1 个上游 float 全局项被 Ghidra 拒绝，游戏结构体均已回读；残留函数／字符串项详见 renkolab 登记与本机日志，未强制覆盖。

## 按旧格式准备

TH08 先参考 [TH06](../th06/README.md) 的旧式脚本处理经验，具体编号和参数以 TH08 原文、专用 map 与本作资料为准。现有合成训练目标仍适用；TH16/TH18 的指令编号、EX 数值与入口约定不能直接套用。

| 位置 | 本作准备口径 |
| --- | --- |
| 执行结构 | `sub SubN()` 与独立 `timeline TimelineN()`；两套 opcode 命名空间分开索引 |
| 时间与难度 | 保留 `+帧数`、跳转时间参数和可能与指令同行的 `!E/!N/!H/!L` 标记；不以文本顺序替代执行顺序 |
| 变量 | 原始引用为正的 10000 起编号；继承变量与非继承变量分开，不能照搬现代局部变量规则 |
| 发弹与 EX | 专用 map 可读名用于导航；111 `etEx(slot,id,async,a,b,r,s)` 等参数须按本作表理解 |
| 回调 | 136 `funcCall(func,param)`、137 `funcSet(func,param)`；Priw8 标注 `-1` 为停用，尚未原生核对 |
| 切分 | 从 timeline 的刷怪与 sub 调用闭包定位攻击；Boss 中断和异步依赖单独带入，暂不生成任务包 |

以上格式来自本次文本；参数解释与变量继承说明来自 [Priw8 TH08 指令表](https://priw8.github.io/#b=modding/&p=ins&table=8)及其 [变量数据](https://github.com/Priw8/priw8.github.io/blob/master/js/ecl/vars.js)，属于社区资料，未声称已经逐项原生验证。查询副本在 `transcribe/work/th08/tools/priw8-th08.json`，包括 185 个 sub 指令条目、17 个 timeline 条目和 100 个变量条目。

既有 th18-leveledit 的 `docs/ECL.md` 记录 TH08 的 x 坐标为 0–384，转到中心原点需减 192，角度为弧度。后续按本卡位置与目标引擎约定转换；本轮未重新调查原生几何。

## 工具诊断与边界

使用既有 thtk release 12 和 [Priw8 的 TH08 map](https://github.com/Priw8/eclmap/blob/master/eclmap/th08.eclm)。24 份 mapped 与 24 份 raw 反编译均退出 0，raw 诊断为空。每份 mapped 有同一条警告：map 把 opcode 5 命名为 `loop`，与 thecl 关键字冲突，名称被忽略；指令仍以 `ins_5(...)` 保留。

其他仍显示原始名称的编号是 79、129、153、173、177、183、184。未命名不等于丢失指令或不可转写，查 Priw8 本作条目及必要原生分支即可，不要求全表逆向。

相邻 th18-leveledit 的 `docs/ECL.md`、`docs/HANDOFF.md` 已记录 TH08 ECL 回编译存在分支偏移问题。本轮只解码原包，没有回编译、替换游戏文件或做原作运行对拍；不要把本次解码成功当成原作补丁链已可用。合成卡后续通过训练引擎编译，不以修复原作回编译器为前置。
