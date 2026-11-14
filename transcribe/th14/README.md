# TH14 转写阶段记录

2026-11-11，按用户要求完成Sol特殊项后，**阶段性结束TH14作者转写**。144个候选中已交付124张草稿：QoderCN 121张为written，Sol 3张通过完整机器检查；另有6个作者阻塞、5个原待补、9个原暂缓。本批尚未完成全批机器验收、独立语义审核或正式收卡，未启动训练。

## 当前结果与搁置项

| 范围 | 数量 | 当前状态 |
| --- | ---: | --- |
| 普通QoderCN | 121 | written；尚未统一完整validate或独立审核 |
| Sol特殊项 | 3 | `th14_s6_b9`、`th14_s6_b10`、`th14_s7_b8`，完整机器检查通过，尚未独立审核 |
| 作者阻塞 | 6 | 下表列明，保留报告及已有草稿，移出默认派发／返工清单 |
| 原待补 | 5 | 保留入口与语义缺口，未派发 |
| 原暂缓 | 9 | 八个曲线激光、一个最近标记弹查询，未派发 |
| 合计 | 144 | 130个已尝试，14个未派发 |

| 阻塞卡 | 实际缺口 | 作者报告 |
| --- | --- | --- |
| `th14_s2_w06` | Hard／Lunatic的Line激光池256耗尽，pool_full分别104／448 | [报告](../work/th14/th14_s2_w06/report.md) |
| `th14_s6_b4` | 动态SIZE影响弹的实际判定，缺逐弹半径／缩放写口 | [报告](../work/th14/th14_s6_b4/report.md) |
| `th14_s6_b5` | 方向调速mode12的s1=.5公式未核，恒速草稿不足 | [报告](../work/th14/th14_s6_b5/report.md) |
| `th14_s6_b6` | mode12语义及动态SIZE写口两项缺口 | [报告](../work/th14/th14_s6_b6/report.md) |
| `th14_s6_b7` | Line激光需要上／左／右反弹，现有激光API无对应配方 | [报告](../work/th14/th14_s6_b7/report.md) |
| `th14_s6_b8` | 玩家判定helper可用；另有弹SIZE从1至1.8，缺逐弹几何写口，未生成省略该行为的成品 | [报告](../work/th14/th14_s6_b8/report.md) |

上述六项均阶段搁置；有元数据的草稿已设 `enabled=false`。未经用户重新决定，不继续调查、重派、审核收卡或启用；不扩池、减弹、缩寿命或删物理机制来接纳。原5个待补与9个暂缓的定位仍见[切分记录](splitting.md#待补与暂缓)，不自动恢复。

Sol实际通过原生子代理完成，使用 `gpt-6.1-sol`／medium，三名作者处理四张卡；不将其记成headless CLI作者批次。第五符保留逐弹迟滞、换色和两段EX；第六符未补源中不存在的REACT；Extra保留每弹一次性的鼓点signal。三卡统一执行：

```bash
uv run --frozen python transcribe/run.py transcribe/work/th14/tasks.sol.json --step check --ids th14_s6_b9,th14_s6_b10,th14_s7_b8 --jobs 3
```

结果3张validated，普通两张覆盖rank0–3、Extra覆盖rank4，错误／警告及运行故障、违约、池满均为0。机器报告在工作区 `logs/20261110T204445.663238Z/` 及各卡同名logs；它们不代表原作逐帧对拍或独立语义审核。普通作者结果见 [Qoder启动记录](../work/th14/current-launch.json)，Sol交付及检查索引见 [Sol记录](../work/th14/current-sol-launch.json)。当前保留清单为121个普通项、3个Sol项，仅供定位既有材料，不构成重跑作者授权。

## 任务包准备

2026-11-09完成本作thdat／thecl解包及Priw8表对照，随后三名Sol完成一至七面[静态切分](splitting.md)；2026-11-10按用户确认合并四、五面道中后，共144候选（64波道中），含40个符卡阶段。2026-11-11初始生成 **130份任务包：126份普通QoderCN、4份特殊Sol**；5个待补、9个暂缓未生成作者包。每份包含task.md、带原行号和边界角色的source.txt、preparation.json；最大源摘录624行。

入口见工作区 [LAUNCH.md](../work/th14/LAUNCH.md)、[逐卡清单](../work/th14/splits/summary.md)、[当前路由清单](../work/th14/generation-report.json)。普通项随后获授权以QoderCN dfmodel、16并发完成126次作者任务；Sol四项按本页上方记录完成。历史批次快照保留原始130项范围，阶段搁置不删除任务源、日志或草稿。

四个特殊包为 `th14_s6_b8`（真实玩家判定）、`th14_s6_b9`（距离迟滞／EX）、`th14_s6_b10`（安装5但不补REACT）、`th14_s7_b8`（一次性鼓点signal）。source与任务给出2.5fx基础玩家半径、signal0独占及恢复／生命周期要求；可行组合和剩余缺口以上方实际交付为准。

任务包准备时，已有校验器和卡库补齐TH14来源识别，沿用现代时限规则；`uv run --frozen pytest -q tests/transcribe tests/test_cards.py` 为190 passed，两份初始清单dry-run通过，130份源摘录已逐节核对原行内容和依赖范围。本次仅对Sol三个完成项运行完整validate，不将旧准备检查当作全批验收。

## 单卡作者入口

作者只处理任务指定的 `task.md/source.txt`，沿以下本作覆写及同包公开手册查阅；下文的持久工程、社区导入和历史原生调查供准备者使用，不要求作者建库或自行逆向。

- 单卡编号、source、外壳、时间与机器检查按[本作验收覆写](validation.md)，普通rank0–3，Extra仅rank4。
- 共用语言／栈／时钟／难度查[TH16基础语义](../th16/mapping.md)，运动、敌与发射器按[TH16专题目录](../th16/README.md#子系统专题)及对应TH18配方；只查本卡所需章节。
- 337按TH14源为 `anmPlayPos`，不套TH18同号含义；作品专用季节和卡牌机制不带入TH14。TH15专项GOTO／BRIGHT例外也不自动套用。
- 弹型使用[TH14词表](touhou-bullets.ecl)；source type0–23对应目标同号、24–42对应目标加1，见[映射](bullet-types.md)。元数据source保持th14。
- [特殊函数](special-functions.md)优先：2号画面操作及恢复省略；3／4号真实判定、5号距离响应、6号鼓点配方按任务明示。现有[判定helper](player-hitbox.ecl)与[signal配方](drum-signal.ecl)按需复制入卡，不能凭helper存在声称整卡已经验收。
- 普通掉落、纯表现、出生阶段、独立波与奖励波按[共用取舍](../th18/transcription-policy.md)。合并波内保留原wait、async和逐创建状态，不在旧小波边界额外清场；真实困难交回准备者，不扩接口／池或任意缩短危险行为。
- 内部LIFE／TIME推进、随机变量、后续EX与依赖按本卡source和入口状态保留；无敌外壳不模拟DPS，不擅自合成固定时刻死亡发弹。原生HP／超时退出与训练尾部预算分别记录，不把收尾余量当成额外持续发射许可。

## 本机材料

- 输入为用户提供的 `transcribe/th14/th14.dat`，工作副本及解包产物在被忽略的 [工作区](../work/th14/README.md)。原包保留原位，不入库。
- 包内有 `th14_0100b.ver`，已提取。2026-11-09 后续已在 renkolab 核对配套 EXE 版本串为 `Double Dealing Character. ver 1.00b`，本作 DAT 与其样本目录中的 DAT 逐字节一致；工程入口见下节。
- 24 份 ECL：`default.ecl`、七关主文件及 Boss／中 Boss 文件；四面另有 `st04bs2.ecl`、`st04mbs2.ecl`。切分时保留两条路线的调用归属，不混合两个文件中的攻击。
- [mapped 源与定义索引](../work/th14/source-context/index.json)：758 个 sub、24,164 行文本，各文件列 ecli 依赖、定义及结束行。
- [raw 指令统计](../work/th14/source-context/opcodes.json)：24,798 条指令、176 种 opcode，保留地址的文本在 `source-raw/`。
- [特殊机制位置](../work/th14/source-context/mechanisms.json)：回调、曲线激光、unknown 及 spec 调用；[章节调用](../work/th14/source-context/chapters.json)共 94 处。这些都是源定义计数，不等于实际执行次数或候选卡数。

## 原生工程入口

2026-11-09 用户授权按 renkolab 既有流程建立 TH14 Ghidra 工程并导入社区 th-re-data。已读该仓 `CLAUDE.md`、`METHOD.md`、`DOCSTYLE.md` 和工具链约定，执行既有 `bootstrap.py th14.v1.00b`，未改共享工具。

- renkolab 登记：`games/th14.v1.00b/INDEX.md`；原样本 `local/th14/th14/` 保留，分析副本在 `local/th14.v1.00b/`。
- 持久工程：`local/th14.v1.00b/ghidra_projects/th14.exe.gpr`，程序 `/th14.exe`；工具用完整版本键 `th14.v1.00b`，避免原始 `local/th14/` 目录遮蔽。
- 离线入口：`local/th14.v1.00b/state/index.html`；模型可读 `state/data/functions.jsonl`，已生成 2,910 个函数页及对应记录。符号回放层为 renkolab 的 `games/th14.v1.00b/symbols.json`。
- 样本 MD5 为 `41a8225e4822f217fb57b4e6530ac593`；重新开库已核对身份，2,910 个 EXE 内函数、135 个游戏结构体、565 个 opcode 标签已回读。
- 社区函数入口与游戏结构体无缺失；12 个 Windows／DirectInput 全局项未套类型，另有 1 项日文字符串识别失败，详情留 renkolab 登记及 `local/th14.v1.00b/audit-setup.json`。

后续优先用同一持久工程和导出；名称、结构和标签仅作导航，沿实际分派、参数和消费者核对所选攻击。不重新建库，不把社区命名当作本作行为已验。

## 与 TH18 的关系

TH14 属于同一现代 ECL 系列，可沿用现有的同步／async、敌级状态、移动、发射器与 EX 的阅读和切分方法。Priw8 的 `main.js` 也通过向早期版本回退实现指令表继承；本次按这个真实继承逻辑展开 TH14／15／16／18 表，没有把空的 `INS_18` 当成无指令。

**可以复用流程及共有说明；尚不能认定为 TH18 的严格语义子集。** eclmap 提供名称，thecl 提供解码，社区继承表提供共通语义参考；三者都不证明本作所有原生分支与 TH18 相同。本轮没有做全表原生逆向，后续只处理影响所选攻击的实际差异。

| 项目 | 本轮发现与接续口径 |
| --- | --- |
| 337 | TH14 为 `anmPlayPos(int,int,float,float,float)`，源有 6 处；TH18 同号是双 int 的 `anmBlendMode`，`anmPlayPos` 移到 338。必须用 TH14 map。 |
| 522／537／539 | 社区展开表有覆写或引用变化；537 的第三参数在早期说明中为 unused，TH16 起写为未解用途。声明符卡仍按 TH14 源理解，不将说明差异自动列成攻击阻塞。 |
| 602 `etSprite` | 已核本作type 0–42的默认ANM／半径／逐色数据；按用户确认提供[合成映射](bullet-types.md)和[TH14词表](touhou-bullets.ecl)。0–23对应目标同号，24–42跳过目标新增的左旋大星弹后对应编号加1。 |
| 632／637 回调 | 已核本作0–6号表项、参数及原生消费关系；用户已确认省略项和处理口径，见[特殊函数](special-functions.md)。完整配方与容量按单卡检查。 |
| 1001／1002 | 源各有 11 处，TH14 map 名为 `spec1`／`spec2`。thecl 的本作参数格式均为 int；TH18 的 1002 则为 float。Priw8 TH14 表没有对应行为说明；不套用 TH16 季节或 TH18 卡牌指令。实际是否影响危险行为需按调用上下文判断，不因缺文档就全表逆向。 |
| EX、激光与变量 | 共有说明作为接续资料；TH18 的 EX 记录容量、版本专用变量、特殊分支与原生地址均不自动变成 TH14 结论。 |

176 种实际使用 opcode 中，展开的社区记录有 5 个编号与 TH18 不同：337、522、537、539、602。这个数字统计文档记录差异，不能理解为“只有五个原生行为不同”；1001／1002 在两版社区说明中均缺失，也不会进入该差异数。完整记录见 [对照结果](../work/th14/source-context/priw8-differences.json)。

另对照现有 thtk `thecl/thecl10.c` 的格式继承表，实际使用 opcode 的参数格式差异为 337 和 1002，见[解码格式对照](../work/th14/source-context/thecl-signature-differences.json)。这也是必须指定 `-d 14`、不能用 TH18 解码替代的直接依据。

## 已定位的特殊机制

用户已确认：2号画面操作直接省略；3／4号保留实际玩家判定变化，复用已有 `set_player_hitbox` 及本作[helper](player-hitbox.ecl)；1／5／6优先现有任务弹或signal，不可行则允许跳过并记录，不扩接口或池。6号的[signal配方](drum-signal.ecl)已备，详见[处理口径](special-functions.md)。

`funcSet` 共 79 处，其中 76 处参数为 0、3 处为非零。2026-11-09已核本作表0为null、632将其写入当前敌回调指针，故0只清当前回调；不能解释成全局重置。0–6号功能及转写边界见[特殊函数](special-functions.md)。

| 源文件／sub | 非零设置 | mapped 行号 |
| --- | --- | --- |
| `st04bs.ecl` / `BossCard2Et1` | `funcSet(1)` | 1020 |
| `st06bs.ecl` / `BossCard5` | `funcSet(5)` | 1449 |
| `st06bs.ecl` / `BossCard6` | `funcSet(5)` | 1614 |

`funcCall` 共 14 处：五面 `funcCall(2)` 10 处，六面 `funcCall(4)` 2 处、`funcCall(3)` 1 处，Extra `funcCall(6)` 1 处，含退场／复位路径。2号发送屏幕合成ANM中断，3／4号设置／恢复玩家大小，6号向活动弹EX槽1注入ACCEL。逐帧1号查询附近标记弹，5号按玩家距离切EX槽。按闭包处理，不按调用数计卡，也不跨作借编号含义。未发现 `funcSet2` 或 `setHitboxFunc` 调用。

曲线激光 `laserCuOn` 共 46 处，分布于四面 Boss／中 Boss 与 Extra Boss／中 Boss 的 10 个 helper 定义。四面两条路线要分别查闭包，不能将 `st04bs.ecl` 的机制直接归给 `st04bs2.ecl`。切分时标出曲线依赖，沿用既有能力边界，具体攻击取舍待切分后确定。

另有 `unknown544` 7 处、`unknown567` 9 处。本次已核567置清SPELLCARD flags的0x100位，消费者尚未穷尽；它是独立指令，不因部分调用紧随 `funcCall(2)` 就合并解释或默认删除。六面第六符虽安装5号，已读闭包未见REACT=1，不擅自补标记使其触发。

## 接续方式与验证范围

攻击已按[本作切分结果](splitting.md)划界，源摘录、入口状态和任务包沿[统一流水线](../README.md)保存。普通攻击使用TH16／TH18共有说明，并由TH14差异覆盖；回调、曲线和实际影响攻击的unknown单独标记。作者阶段现已结束，后续整批验收、独立审核、收卡或恢复搁置项均按用户后续决定，不自动派发或启动训练。

源准备时 `thdat -x14` 提取成功，24份mapped和24份raw反编译均退出0，48份诊断日志为空；ecli依赖齐全，定义行号与结束行已核，本地TH14 map与当次GitHub原文逐字节一致。未做回编译、原作逐帧对拍或全表原生语义验收；本阶段机器检查的实际范围见顶部记录，未启动训练。

社区资料取用日期为 2026-11-09：[TH14 eclmap](https://github.com/Priw8/eclmap/blob/master/eclmap/th14.eclm)、[指令数据](https://github.com/Priw8/priw8.github.io/blob/master/js/ecl/ins.js)、[变量数据](https://github.com/Priw8/priw8.github.io/blob/master/js/ecl/vars.js)、[继承逻辑](https://github.com/Priw8/priw8.github.io/blob/master/js/ecl/main.js)。原文副本及展开表留 work，不入库。
