# TH18原生语义与参数来源

整理：2026-11-17。保留TH18 v1.00a的原生地址、关键参数来源和编号纠错；规则用法以[TH18指南](../../transcribe/th18/README.md)及专题为准。以下为已做核查的证据，未覆盖的分支不据此提升为已核。工具版本与社区来源见本节末，旧本机路径可能已消失，优先复用renkolab持久Ghidra和导出。

## lasers.md：原生依据/历史验证

宽度分段依据已有[TH18 几何调查](2026-10-22-th18-geometry/encoding-lasers.md)记录的原生 Listing：Line `0x44aa25..43`、Infinite `0x44ced4..f5` 与几何消费者 `0x45cea0`。原作玩家使用局部矩形，与目标玩家圆形相交仍有独立判定差异；匹配激光矩形不等于完整碰撞等价。

## instructions.md：带地址的原始说明

| opcode / 精确助记名 | 功能与路径 | 处理及边界 |
|---|---|---|
| 0 `nop` | 无副作用占位；保留其时间门 | `drop` 只删操作，不删等待 |
| 1 `delete` | 结束当前上下文；敌主上下文结束使敌静默退场 | `translate`：目标结束当前任务；额外async结束不等于敌死，不能统一换 `die()`；见教材 §3.2 |
| 10 `ret`；11 `call` | 同步返回/调用，源保存调用时钟与栈帧 | `translate`：静态非递归call图改普通sub，参数/时间先恢复；根ret为结束。目标禁递归，不能直接保留无限尾调用链 |
| 12 `jmp`；13 `jmpEq`；14 `jmpNeq` | 分支/跳转还写源脚本时间；13判零、14判非零 | `translate`：按执行轨迹写if/while/goto+wait；不能仅保留PC跳转。教材 §3.1；本作VM `0x48b3a0` |
| 15 `callAsync` | 同敌新增上下文、拷实参 | `translate`：`spawn helper(...)`，目标次帧首跑；同敌共享I/F不变成任务局部快照。教材 §3.2–3.3 |
| 16 `callAsyncId`；17 `killAsync`；21 `killAllAsync` | 同敌async带用户ID创建、查ID取消、全async取消 | `需上下文`：有限已知集合可显式保留目标任务标识；源ID不是目标池索引，`KILL_CHILDREN`只及直系，不能覆盖同敌孙任务。一般动态ID取消 `blocked`；见[状态表 §4](../../transcribe/th18/enemy-state.md#4-同一敌人的段入口恢复状态而非重置模板) |
| 23 `wait` | 推迟源脚本时间门 | `translate`：正常dt=1且整数等待可恢复为目标wait；与时间标签不可双算。教材 §3.1 |
| 24 `waitf`；547 `gameSpeed` | 浮点等待/游戏速度影响源时钟 | `需上下文`；确有子帧或变速要求时无一般等价目标内建，`blocked`，不能默默取整 |
| 40 `stackAlloc`；42 `pushi`；43 `seti`；44 `pushf`；45 `setf` | 原生局部/表达式栈读写 | `translate`：先恢复高层变量与求值顺序再写var/赋值；`[-1]`并非每次独立pop。教材 §2.1、§3.4 |
| 50 `addi`、51 `addf`、52 `subi`、53 `subf`、54 `muli`、55 `mulf`、56 `divi`、57 `divf`、58 `modi` | 标量算术 | `translate`：int/fx/angle按物理量拆分，整数除法与float表达式不能混写；教材 §2.2 |
| 59 `eqi`、60 `eqf`、61 `neqi`、62 `neqf`、63 `lessi`、64 `lessf`、65 `leqi`、66 `leqf`、67 `greateri`、68 `greaterf`、69 `geqi`、70 `geqf` | 比较 | `translate`：比较前保留源类型、角规范化与表达式副作用 |
| 71 `noti`；72 `notf`；73 `or`；74 `and`；78 `deci` | 逻辑操作与自减 | `需上下文`：恢复原操作数求值后再写条件；目标&&/\|\|短路可能少消耗RAND，自减要保留旧值用途 |
| 75 `xor`；76 `bit_or`；77 `bit_and` | 整数逐位操作 | `需上下文`：不能把一般掩码改成逻辑布尔；常量可在转写时算出，动态完整位运算的目标配方未在本表证明 |
| 79 `stackSin`；80 `stackCos`；81 `circlePos`；82 `validRad`；83 `negi`；84 `negf`；85 `squareSum`；86 `squareSumRoot`；87 `getAngle`；88 `stackSqrt` | 数学/插值定位组 | `需上下文`：普通三角/向量可用sin/cos/atan2/dist；弧度先转BAM。89名字不能当“线性乘法”的证据；91/92任意变量写回、93随机分布及88一般sqrt尚无本表完整TH18配方，实际需要且本书未定义时交主会话补齐，插值见[模式表](../../transcribe/th18/interpolation-modes.md) |
| 89 `linearFunc`；90 `pointRotate`；91 `floatTime`；92 `math92`；93 `math93` | 数学/插值定位组 | `需上下文`：普通三角/向量可用sin/cos/atan2/dist；弧度先转BAM。89名字不能当“线性乘法”的证据；91/92任意变量写回、93随机分布及88一般sqrt尚无本表完整TH18配方，实际需要且本书未定义时交主会话补齐，插值见[模式表](../../transcribe/th18/interpolation-modes.md) |

| opcode / 精确助记名 | 功能与路径 | 处理及边界 |
|---|---|---|
| 600 `etNew` | 初始化指定et配置及辅助偏移/游标状态 | `translate`：在负责发射的目标任务里sh_reset，再显式写实际需要的字段；源16份配置、目标每任务4槽，不能直接全保留默认值 |
| 601 `etOn` | 读取当前配置建弹 | `translate`：sh_fire或按原序显式fire；出生角/速度/顺序/随机范围见教材 §5与[瞄准表](../../transcribe/th18/aim-modes.md) |
| 602 `etSprite` | 弹型与色 | `translate`按[弹型表](../../transcribe/th18/bullet-types.md)，源type不是目标appearance |
| 603 `etOffset`；626 `etOffsetRad`；627 `etDist`；628 `etOffsetAbs` | 出弹位置/距离配置定位 | `需上下文`：先恢复实际出生点与坐标层；603常见偏移用sh_offset，628/626/627不能都当同一个offset。自机狙从实际口算 |
| 604 `etAngle`；605 `etSpeed`；606 `etCount`；607 `etAim` | 方向、首末速度、颗数/层数与模式 | `translate`：sh_angle、sh_speed、sh_count、sh_aim/sh_ring；源首末速度须转层步长，见教材 §5与瞄准表 |
| 608 `etSound` | 发射声音配置 | `drop`限不参与所选攻击逻辑的音效 |
| 609 `etExSet`；610 `etExSet2`；611 `etEx`；612 `etEx2` | 指定槽/追加短长EX记录 | `translate`/`blocked`逐EX判断；短式不清未写字段，24条EX与追加游标要保存，见[EX表](../../transcribe/th18/ex-effects.md)、教材 §6 |
| 614 `etCopy` | 复制源et描述符及辅助偏移到目标et | `需上下文`：TH18本作0x430d30 case0x7f复制0x488字节及两组偏移；不写单独EX追加游标。目标无sh_copy；有限静态字段可缓存重放，不能以sh_reset(dst)代替拷贝，更不能顺手清游标 |
| 613 `etClearAll` | 全场普通弹及激光取消 | `需上下文`：本作handler调BulletManager与LaserManager取消，**不是清空et配置**。目标clear_bullets是field，执行相位/激光/转星规则有差别 |
| 615 `etCancel`；616 `etClear` | 敌位置圆域取消，原handler传不同mode | `需上下文`：候选clear_bullets_at；半径、道具、激光部分取消和相位要对齐，本表未补全TH18取消消费者，不能直接套TH16转星规则 |
| 635 `etCancel2`；636 `etClear2`；712 `etCancelRect` | 其他圆域/矩形取消入口 | `需上下文`：712已核只处理普通弹矩形域，不是改弹判定；635/636逐样本核过滤，目标field不能自动覆盖源保护规则 |
| 617 `etSpeedR3`；618 `etSpeedR5`；619 `etSpeedR2`；620 `etCountR3`；621 `etCountR5`；622 `etCountR2`；624 `etSpeedD`；625 `etCountD` | 按rank/难度选值的配置入口 | `需上下文`：固定难度可先消解已核分支；原动态RANK不等于目标GVAR_RANK。教材 §3.3 |
| 623 `angleToPlayer`；640 `etExSub`；641 `etExSubtract` | 角度查询及EX相关定位 | `需上下文`：623从实际取样位置/时点核方向；640/641不得仅凭名当已支持EX重排 |

## enemy-state.md：带地址的原始说明

| 原位 | 已核消费者/行为 | 转写边界 |
|---|---|---|
| `0x2` | `0x42ed40` 体碰入口检查 `flags & 0x22 == 0`；受击入口检查的是 `flags & 0x21` | 仅这一位的禁体碰用途可表达为 `ENEMY_NO_BODY`，清位反向映射；同时存在其他禁体碰原因时不能盲目清目标位 |
| `0x4` / `0x8` | `0x42e5a0`分别跳过横/纵屏外回收；五面首符flag303实际同时使用 | 目标敌仍有出界回收。无交互、无其他实体查询的发射体可按值任务保存独立世界坐标，见[五面首符](../../cards/th18/th18_s5_b2/notes.md) |
| `0x10` | 同函数伤害扣血路径要求该位为0且无敌计时器到期 | 只核到阻止扣血；`set_invuln` 有期限且目标事件行为不同，不等于复制整位 |
| `0x20` | 同时进入受击门 `0x21` 与体碰门 `0x22`；502/503还遍历ANM做状态操作 | 同时影响交互及动画，不能只解释成禁体碰或纯外观；按样本拆出必要行为 |
| `0x1000` | 伤害路径选择圆/宽高分支；体碰也切到另一几何路径 | 不能作为目标公开 flag 写入；形状/朝向按实际消费者核 |
| `0x20000` | 移动限位开关，504写入四边界并置位，505清位 | 目标无常驻限位写口，见 §3 |
| `0x80000` | 镜像开关；424按参数置清，创建helper也读取 | 保存在脚本状态；按具体移动指令与创建顺序处理，见 §2–3 |

目标公开可写另有 `ENEMY_KILLALL_EXEMPT`，但本文未确认一个能覆盖 TH18 所有清场入口的单一源位。原生清场 `0x430710/0x430910/0x430b20` 检查复合掩码 `0xc004a0`，并有 `0x100` 例外；不能从 TH16 表拷一个位号就声称等价。

`0x4369e0` 中，若父 `0x80000` 置位，在按[创建变体规则](../../transcribe/th18/enemy-state.md)加父坐标之后再把最终出生x取负，并翻转子镜像初始位；y保持前一步结果。于是普通相对创建在父镜像下的x是 `-(parent_final_x + input_x)`，不能改成 `parent_final_x - input_x`。这是创建helper的静态事实，不应外推为所有移动或发弹指令的统一镜像规则。F族检查在 `0x430d30` 的共享分派分支中，找到boss0则不执行普通创建路径；不要凭F名字解释为“继承全部flags”。

旧 `renkolab/engine/ecl/th18/05-stage1-midstage-spawns.md` 的创建变体表存在错位与“A=async”的旧说明；本表以当前eclmap及本作 `0x4369e0` 为依据，不沿用该解释。

TH18有ABS与REL两套PosVel状态，并由 `0x42ec00` 合成最终位置。`402 movePosRel` 是写REL层，不能泛化为“给当前世界位置加一段偏移”。两层都在运动、插值未结束或读回ABS/REL变量时，单次 `move_to` 无法保留这些状态。

- **573 unknown573、574（thecl显示ins_574，eclmap未命名）**：handler分别为 `0x433a4a`、`0x433a70`，调用 `0x42d020/0x42d040` 写限时额外掉落及窗口/计时。已有renkolab `engine/ecl/th18/02-item-drops.md` §5.1–5.2也已说明；这些属于击破速度奖励掉落，不是等待/发弹配置，按普通道具省略。
- **569 unknown569、570 unknown570**：handler `0x4338ab/0x433904`。569写敌 `+0x6828` 的章内计数权重，调用 `0x439ec0` 增加统计；570在自身chapter匹配当前chapter时，经 `0x439eb0` 结算并清零该权重。对应写口只累加章节统计字段，未写运动/发射配置。更上层评分用途未完整追踪，但不因其unknown名字阻塞Stage01独立攻击切分。
- **401 movePosTime在frames≤0时**：分派走 `0x431bbf`，调用 `0x439900` 只清该位置插值的持续字段；本支不把参数x/y写成当前坐标。因此Boss换段的 `movePosTime(0,0,0,0)` 不能改成目标 `move_to(0,0fx,0fx,...)` 瞬移。后续正时长移动仍从当时位置起步。
- **525 enmKillAll与死亡回调**：分派经 `0x434e1b` 调 `0x430710`，对通过源flag过滤的敌调用 `0x430240`；该函数执行非空setDeath程序。不能把原作清敌都解释成无回调静默删除。571的另一清场路径 `0x430b20` 则先清回调字符串。源事实已能区分；训练交接是否保留这些尾部按[用户已批准口径](../../transcribe/th18/transcription-policy.md#系统性省略与外壳接管)，不再要求逐帧复现跨波过程。

## movement.md：带地址的原始说明

412的参数依次是持续帧数、角插值mode、起始速度。`0x433375`选择ABS角槽与速度槽；`0x4335ff`起读取mode、speed和duration。每次调用使用当时FINAL位置和玩家x，得到一个固定方向α。

设`R = π×U`，U为有符号单位随机量。`0x405b90`调用`0x402810`后在`0x405b99`再乘π；不能把R直接当U。横向分支见[moveRand配方](../../transcribe/th18/movement.md)，条件为严格小于/大于。

随后按y处理：y<112取`α=abs(α)`；y>144取`α=−abs(α)`；112≤y≤144不动。**中央加π后没有先wrap**，必须保留这个顺序；例如α=200°时顶部的abs仍为200°，不能提前转成−160°再取abs。左右外侧分支只有右侧显式wrap。证据：`0x4333c9`–`0x433563`。

最后，若`abs(α+π/2)<0.05`，按原来位于−π/2的哪一侧推至`−π/2±0.05`；否则若`abs(α−π/2)<0.05`，同理推至`π/2±0.05`。恰等中心时选加0.05一侧。没有额外随机。按上述方向区间，本卡实际不会接近±90°，因此该护栏保留在配方中但本样本不可达。证据：`0x43356b`–`0x4335f7`；常量分别读到±1.520796…、±1.620796…。

`0x42e5a0`先推进角/速插值，转换当前极坐标速度并积分ABS、REL，再调用`0x42ec00`组合FINAL。`0x42ec77`–`0x42ecf9`对FINAL夹界，`0x42ed03`–`0x42ed2e`将ABS写回`FINAL−REL`。不改速度、方向或插值进度；被挡住的位移不会积在墙外，也不会反射。本卡REL恒零，递推公式见[moveRand配方](../../transcribe/th18/movement.md)。

`0x42ff80`依次执行运动/限位、Enemy__ecl_run、EnemyData__step_game_logic（含体碰）：即**源为移动→ECL→体碰**。因此配置moveRand的那一次发射仍从旧位置P(0)出弹，后续源t+1读到P(1)，源t+5读到P(5)。本卡t0先清速度/旧插值，60帧移至(0,128)，t90才开始moveRand；独立训练已选择(0,128)初始化时，初次回中是零位移。

## aim-modes.md：带地址的原始说明

> **版本**：TH18 v1.00a。裸地址属于本作；2026-11-05复用既有Ghidra导出核查。
> **方法**：`FUN_00424fe0` `0x424fe0` 的逐弹分支，加包装 `FUN_00427810` `0x427810`；Priw8教程作交叉参照。

TH18 `0x424fe0` 的case11/12确实使用表列环角；然后调用 `FUN_004a9ea0`，
再以绝对值参与速度调制。现有Ghidra反编译未正确表达该调用的SSE参数/返回，
不能将残留的 `(1-abs(angle)*s1)*v(q)` 当作已核公式，也不能因社区称“peanut”就自行补sin。
未解点只在这两行的方向调速函数及其s1有效域；0..10不因此整体待定。

## interpolation-modes.md：带地址的原始说明

> **版本**：TH18 v1.00a；2026-11-05整理。裸地址均属本作。
> **证据**：已核的原生归一化函数 `0x402fb0`、分派 `0x4035d8`，以及标量 `0x41f640`、运动 `0x439a00` 消费者；复用引擎既有核查，未重新逆向。

普通`405 moveVelTime`（ABS；407是moveVelRelTime/REL）的角度插值取最短弧：当前与目标差的绝对值≥π时，给较小端点加2π后插值。父变量分别`validRad`不会使其改走长弧。TH18指令`0x432388–0x4323d8`及π/2π常量已于2026-11-06只读核实；五面首符的160°/−170°转向使用此规则，不外推mode7/8等特殊分支。

## ex-effects.md：带地址的原始说明

| type 十六进制 / 十进制 int | 效果 | 参数语义 | 与 TH16 对照 |
|---|---|---|---|
| `0x1` / 1 | [SPEEDUP](2026-11-05-th16-th18-ex-comparison.md#ex-1) | 已核主路径无参数 | 相同（已核子集） |
| `0x2` / 2 | [ANIM](2026-11-05-th16-th18-ex-comparison.md#ex-2) | a=ANM interrupt=7+low16(a) | 相同（已核子集） |
| `0x4` / 4 | [ACCEL](2026-11-05-th16-th18-ex-comparison.md#ex-3) | a=持续时间；r=加速度标量；s=角参数；各版本解析不同；m=TH18瞄准偏移/随机幅度；TH16瞄准偏移见既有一手记录 | 不同 |
| `0x8` / 8 | [ANGLE_ACCEL](2026-11-05-th16-th18-ex-comparison.md#ex-4) | a=持续时间；r=速度增量/帧；s=角速度；每步 angle += s*dt | 相同（已核子集） |
| `0x10` / 16 | [STEP / ANGLE](2026-11-05-th16-th18-ex-comparison.md#ex-5) | a=每段持续时间；b=段数上限；c=角/速子模式0..7；d=保存进私有状态；本轮未确定用途；r=角参数；c=5/6为随机幅度；s=目标速；<=-999990保留；c=7为当前速随机幅度；m=TH18角helper偏移/幅度 | 不同 |
| `0x40` / 64 | [BOUNCE](2026-11-05-th16-th18-ex-comparison.md#ex-6) | a=反弹事件次数上限；b=墙mask U/D/L/R=1/2/4/8；0x10抑制反射；0x20自定义尺寸；r=> -990时设置反弹处理后的speed，否则保留；s=b&0x20时宽；否则384；m=b&0x20时高；否则448 | 相同（已核子集） |
| `0x80` / 128 | [INVULN](2026-11-05-th16-th18-ex-comparison.md#ex-7) | a=写入bullet+0x24计数 | 不同 |
| `0x100` / 256 | [OFFSCREEN](2026-11-05-th16-th18-ex-comparison.md#ex-8) | a=最长保活倒计时；b=非0额外做视锥可见性检查 | 相同（已核子集） |
| `0x200` / 512 | [SETSPRITE](2026-11-05-th16-th18-ex-comparison.md#ex-9) | a=弹型索引；b=低15位颜色；0x8000触发ANM interrupt2 | 相同（已核子集） |
| `0x400` / 1024 | [DELETE](2026-11-05-th16-th18-ex-comparison.md#ex-10) | a=等于1时先把cancel script设-1 | 相同（已核子集） |
| `0x800` / 2048 | [PLAYSOUND](2026-11-05-th16-th18-ex-comparison.md#ex-11) | a=声音id | 相同（已核子集） |
| `0x1000` / 4096 | [WRAP](2026-11-05-th16-th18-ex-comparison.md#ex-12) | a=传送次数上限；b=墙mask U/D/L/R=1/2/4/8 | 相同（已核子集） |
| `0x2000` / 8192 | [SHOOTPREP / SHOOT](2026-11-05-th16-th18-ex-comparison.md#ex-13) | a=aim模式；b=子弹起始effect_index；c=路数；d=层数；r=发射角/当前角/玩家角哨兵；s=第二角；m=首速；<=-999990保留父speed；n=末速 | 不同 |
| `0x4000` / 16384 | [SHOOT_DATA](2026-11-05-th16-th18-ex-comparison.md#ex-14) | a=配对记录：sprite；b=配对记录：color；c=配对记录：非0删除父弹 | 相同（已核子集） |
| `0x8000` / 32768 | [REACT](2026-11-05-th16-th18-ex-comparison.md#ex-15) | a=写入反应编号字段 | 未核（消费者） |
| `0x10000` / 65536 | [GOTO / LOOP](2026-11-05-th16-th18-ex-comparison.md#ex-16) | a=目标EX记录index；b=<=0无条件跳；>0使用逐弹共享循环计数 | 相同（已核子集） |
| `0x20000` / 131072 | [MOVE](2026-11-05-th16-th18-ex-comparison.md#ex-17) | a=持续时间；b=低8位插值模式；0x100相对坐标；r=目标x；s=目标y | 相同（已核子集） |
| `0x40000` / 262144 | [VEL](2026-11-05-th16-th18-ex-comparison.md#ex-18) | r=<-990保留角；[-990,990)字面；>=990朝玩家+r-999；s=<-990保留speed，否则直接赋speed | 相同（已核子集） |
| `0x80000` / 524288 | [VELADD](2026-11-05-th16-th18-ex-comparison.md#ex-19) | a=写私有时限；r=附加位移方向；s=附加位移速度 | 相同（已核子集） |
| `0x100000` / 1048576 | [BRIGHT](2026-11-05-th16-th18-ex-comparison.md#ex-20) | a=1/2选择混合标志，其余清相应模式位 | 相同（已核子集） |
| `0x200000` / 2097152 | [VELTIME / ACCELWEIRD](2026-11-05-th16-th18-ex-comparison.md#ex-21) | a=持续时间/计算斜坡的分母；r=目标标量速；s=角参数；各版本解析不同；m=TH18瞄准偏移或随机幅度 | 不同 |
| `0x400000` / 4194304 | [SIZE](2026-11-05-th16-th18-ex-comparison.md#ex-22) | a=插值结束时间；b=插值模式；r=初始尺寸；s=最终尺寸 | 相同（已核子集） |
| `0x800000` / 8388608 | [SAVE / SAVEANGLE](2026-11-05-th16-th18-ex-comparison.md#ex-23) | 已核主路径无参数 | 相同（已核子集） |
| `0x1000000` / 16777216 | [ENMCREATE / ENEMY](2026-11-05-th16-th18-ex-comparison.md#ex-24) | a=子敌I0；b=子敌I1；c=子敌I2；d=子敌I3；r=子敌F0；s=子敌F1；m=子敌F2；n=子敌F3 | 相同（已核子集） |
| `0x2000000` / 33554432 | [LAYER](2026-11-05-th16-th18-ex-comparison.md#ex-25) | a=渲染桶/层索引 | 相同（已核子集） |
| `0x4000000` / 67108864 | [DELAY](2026-11-05-th16-th18-ex-comparison.md#ex-26) | a=等待时间；<1直接前进 | 相同（已核子集） |
| `0x8000000` / 134217728 | [LASER](2026-11-05-th16-th18-ex-comparison.md#ex-27) | a=0线激光；1无限激光；其他值不创建；b=sprite；c=color；d=a0:非0删除父；a1:flags及起始effect_index/删父打包；r=角/哨兵；s=speed/保留哨兵；m=线:长度；无限:附加浮点字段（未核命名）；n=线:长度相关字段；无限:长度 | 不同 |
| `0x20000000` / 536870912 | [HITBOX](2026-11-05-th16-th18-ex-comparison.md#ex-28) | r=>=0为动态半径；<0恢复当前弹型默认半径 | 相同（已核子集） |
| `0x80000000` / -2147483648 | [WAIT](2026-11-05-th16-th18-ex-comparison.md#ex-29) | a=等待时间；<1直接前进 | 相同（已核子集） |
| `0x40000000` / 1073741824 | [HOMING（行为别名）](2026-11-05-th16-th18-ex-comparison.md#ex-30) | a=持续时间；r=目标速度；s=瞄准角偏移；m=每步速度向量混合系数 | TH18新增 |

原生`0x423e10`在任一handler返回结束后，会同帧重新执行整列active效果，最后只积分一次位置；`0x428970`的OFFSCREEN每次调用都减1。因此保活参数不能总按世界帧原样复制。二面第二符两个效果结束各多减一次，300对应目标298帧；三面首符五次边界让200在零起age194清位，该帧还会让正在运行的VELTIME多更新一次。按具体效果链折算，配方见成品[二面第二符](../../cards/th18/th18_s2_b4/notes.md)和[三面首符](../../cards/th18/th18_s3_b2/notes.md)；此前二面首符的同长ANGLE_ACCEL200/OFFSCREEN200仍用200。

STEP 的已核降速分支在第 t 次更新（0≤t<a）使用**当时的标量 speed**：`v_draw = speed - t*speed/a`，再用当前角构造本帧速度；这个计算读取原作当前逻辑标量，向量构造 helper `0x429bc0` 本身不回写标量；没有其他效果改它时，该段就是固定逻辑速率乘线性下降系数。段界恢复保存的目标 speed、更新角、计数加一并重置段计时。c0/5 加偏角，c1/6 在段界重新查玩家，c2/c3 依赖 SAVE，c4 固定目标角；c5/6/7 另有随机及进入解析顺序。

## lasers.md：带地址的原始说明

| 编号 / 名称 | 原作签名与参数 | 本作关键含义 | 目标路径 |
|---|---|---|---|
| 700 laserNew | `Sffff (etId, initialLength, targetLength, lengthLimit, width)` | 配发射器激光几何；第三浮点在线激光限制末端路程 | `laser` + `lz_start/lz_speed`，先换算实际判定段 |
| 701 laserTiming | `SSSSSS (etId,startup,expand,hold,shrink,flags)` | Infinite 四段；Curve 把 startup 槽用作轨迹长度 | 静态宽度子集转三段时长；扩宽期见[激光专题](../../transcribe/th18/lasers.md) |
| 702 laserOn | `S (etId)` | 创建 Line，复制发射器 EX | 飞棒/增长线组合；无通用 EX 复制入口 |
| 703 laserStOn | `SS (etId,laserId)` | 创建 Infinite 并给实例编号 | 保存 `laser()` 返回句柄 |
| 704 laserOffset | `Sff (laserId,x,y)` | 写当前原点及保存的基点；本作函数 `0x42d700` | `lz_origin`；若依附敌人则明确使用 `lz_anchor` |
| 705 laserTrajectory | `Sff (laserId,x,y)` | 写 Infinite 的附加向量 `+0x794/+0x798` | 按本作每 tick 原点公式组合；不能直接当持续匀速平移 |
| 706 laserStLength | `Sf (laserId,value)` | 写 `+0x78`：长度增长速率，不是立即设总长度 | 有限增长路径可评估 `lz_speed`，注意它会重设 end |
| 707 laserStWidth | `Sf (laserId,width)` | 写当前宽 `+0x74`；phase 随后可能再次覆盖 | 目标无当前宽度写口，不能直接还原动态改宽 |
| 708 laserStAngle | `Sf (laserId,angle)` | 写当前角 `+0x6c`，单位弧度 | 用当前 `lz_angle` 算差后 `lz_rotate` |
| 709 laserStRotation | `Sf (laserId,omega)` | 写角速度 `+0x7a4`，tick 持续积分 | `lz_omega`，弧度/帧转 BAM/帧 |
| 710 laserStEnd | `S (laserId)` | 找到该编号实体，调用取消并解除编号，循环至无匹配 | `lz_cancel`；原作同编号多条须保存全部句柄 |
| 711 laserCuOn | `S (etId)` | 创建 Curve，保存逐段运动历史 | 暂不转写；命中曲线依赖则blocked |
| 712 etCancelRect | `ff (w,h)` | 以当前敌位置取消矩形内普通弹 | 不能当作“清所有激光”；目标清弹形状另核 |
| 713 unknown713 | `SS (etId,laserId)` | 分派调用激光 kind=3 的分配路径 | kind=3 后续实体消费者未核，不能宣称可用 beam |
| 714 unknown714 | `SS (laserId,value)` | 找实体后调用 vtable+8，传第二参数 | 未核该调用具体行为；无确定目标映射 |

705 尤其容易误读：Infinite tick `0x44cae0` 每帧先从保存基点恢复当前原点（特定 flags 下改用 boss0 位置），然后加一次该向量乘 dt，再加沿当前角的距离偏移。仅凭社区“每帧移动”的描述，把 `(x,y)` 连续累加到世界原点，会产生本作没有的漂移。这里已核公式顺序，但这些 flags 的完整用途及所有来源指令仍未全解。

这是本作 `LaserLine__check_graze_or_kill 0x44a950`、`LaserInfinite__check_graze_or_kill 0x44ce80` 的几何。Line 另有 `L>16` 与 `w>3` 门；Infinite 要 `L>16` 且处于原生状态 2 或 4。目标没有这些原作数值门，短小激光不得不经判断就设成 active。

## conversion-examples.md：带地址的原始说明

这不是 TH06 `jump_dec` 的移植。TH18 的依据是既有原生导出 `EclRunContext__ecl_run 0x48b3a0`：opcode12 写当前脚本时间并跳 PC（Listing `0x48b700`），13/14 条件满足时走相同路径；23 的 wait 则减当前脚本时间（`0x48b727`），下一条指令的时间门决定何时继续。现有[导入原型](../../tools/th18-import-prototype/README.md#时间和栈的转换)用 `clock=$frame-base` 表达这套规则，goto 对应 `base=$frame-newTime`，wait 对应 `base+=n`。不要套 TH06 变量拷贝或自动计数规则。

首跑相位并非仅凭目标习惯假定：原生 `Enemy__ecl_run 0x48d420` 在运行当前栈前缓存 next；`0x48d850` 把新 async 插在主节点之后。主任务本帧新增的 async 不在已缓存的遍历链上，所以本例 `shoot` 下一 tick 首跑。在已有 async 或后续 async 再生任务等复杂结构中，仍须按链顺序核查，不能推广成所有创建都相同。

依据 `LaserInfinite__initialize 0x44c870`、`LaserInfinite__on_tick 0x44cae0`、管理循环 `0x448760`：出生状态3，timer=0；每tick先执行状态分支，再由管理循环递增timer。按固定dt=1、无冻结，且以出生后第一次激光tick为 age=0：

## 试用后同步：普通圆体碰半径

Sol试用指出enemy-state仍保留早期“体碰换算未核”。[首卡试产记录](2026-11-05-th18-first-card-trial.md)的“首次worker阻塞后主会话补核”已记录：TH18普通圆分支从EnemyData+0x118取体碰宽度、乘0.5后传给碰撞函数；body48×48对应r=24。原地址/常量及Listing定位见该记录的普通圆体碰半径依据。2026-11-07将这一已核普通分支同步到规则书，明确24×24对应r=12；不外推矩形、旋转或自定义判定，没有重新逆向或新增近似。

## 405与407的编号纠正

2026-11-07，用户要求核清插值章节的“407 moveVelTime”。本机TH18 eclmap明确为405 moveVelTime（ABS）、407 moveVelRelTime（REL）。五面首符原文st05bs:638/640/642/644使用moveVelTime，故实际为405；旧试产记录、审核说明及教材将其记成407，历史记录中的这一编号应按此纠正。

主会话只读既有renkolab `local/th18.v1.00a/state/data/functions.jsonl` 中addr=00430d30的导出：case 0x19是压缩跳表的内部case号，不是ECL opcode；该处理按原opcode 0x195（405）选择ABS状态，REL分支使用另一组状态，镜像条件同时识别0x195/0x197（407），之后共用角差处理。旧 `transcribe/work/th18/stage05/th18_s5_b2/review-main/short-arc.listing.txt` 的0x432388–0x4323d8及short-arc-read.log确认绝对角差与π比较、给较小端点加2π。两者普通分支的最短弧结论成立，纠正的是编号/名称和样本归属；不新增对mode7/8、全部镜像或其他特殊组合的承诺。

本次未新开逆向工程或修改引擎、卡代码，也未重跑训练/卡验收。规则正文只保留名称、层归属及可用结论。

## 三层参考结构与参数来源核对

2026-11-07，用户确认一份指令表、一份总体纲要、各子系统专题。`instructions.md`改为原作参数字典，`README.md`管总体模型和查询顺序；旧索引中的转换限制归入基础语义、敌状态、移动、发射器及EX专题。专题的可编译教学程序保持不变，EX／激光的重复签名表改为链接唯一指令表。

参数名称对照本机eclmap（f146162e330c27d1b0a8880c3a41884615147a11）与当日读取的Priw8 `js/ecl/ins.js`；参数类型另核本机thtk（892114a0fcaa0bbdaaecf3cb4ad56f758683fb40）的TH18格式回退链。社区继承条目单独标注，不提升为TH18原生全验证。本轮没有新逆向、模型调用或原作动态对拍。

- 91/92变量插值参数和上下文归属来自既有引擎公开参考 `docs/stateful-interpolation-reference.md`；91配置写start及帧尾推进来自二面首符已核记录，已回填插值专题。
- 92语义为八参，但本机thecl格式只有 `SfSSff`；713已有本作／社区两参记录，但本机thecl格式为 `S`。指令表保留冲突，不更改工具或推断缺失值。普通六面保留文本没有math92调用；未知输入是否受此影响需准备时判断。
- 完整性检查以本机eclmap的315个名字加94/574两条未命名指令为范围，共317条；这表示可查条目数量，不表示全部语义或目标支持已核。
- 已批准的掉落省略和STEP单段特例已同步到摘要，避免旧限制覆盖新结论。原作参数定义、目标配方和历史调查继续分工维护。

## 补充原生证据

以下地址仍只适用于TH18 v1.00a。

原作固定来源：`/data/sunyunbo/www/renkolab/local/th18.v1.00a/state/data/functions.jsonl`。关键记录：748 `0x42e100` 构造；749 `0x42e5a0` 双层推进/出界；751 `0x42ed40` 受击、flags与体碰门；754 `0x42ff80` tick顺序/计时器；760 `0x430d30` handler；761 `0x4369e0` 创建和12槽快照；1459 `0x48b3a0` VM；1460 `0x48d420` 主/async结束。地址为TH18 v1.00a；JSONL行号随重新导出可能变化，优先用地址。

- [结构化核查记录](2026-11-05-th16-th18-bullet-types.json)：两作 exe、ANM、Ghidra 导出 SHA256、逐型数据及对照结果。
- TH16 已命名 Ghidra 导出：`bullet_pool_spawn`（`th16:0x412cb0`）读取 `g_bullet_render_desc + type*0x114`；主脚本在 `+0x0`，基础半径在 `+0x104`。符号落盘脚本为 renkolab `tooling/ghidra/scripts/apply_th16_bullet_names.py`。
- TH18 表基址 `th18:0x4c5f90`，stride `0x118`；初始化在 `th18:0x425992` 附近读半径，换型在 `th18:0x42640a` 附近重读。本机 `docs/investigations/2026-10-22-th18-geometry/` 的既有 48 项几何核查与本轮全部数值一致。旧报告及 CSV 仍是本机未入库资料，主要数字与出处已保存在上述本轮 JSON。
- 本轮使用项目已有 `tooling/pe_read.py` 读常量数据，复用 Ghidra 与标准 thtk 的既有导出；没有自行反汇编、重建数据库、复制原作资产入库或运行游戏。

原生依据：setter `0x432899` / `0x4329b3` / `0x432cdd`；状态推进 `0x402bf0`；坐标消费者 `0x402cc0`，椭圆分支 `0x402d64–0x402e0e`；角差helper `0x404c70`；FINAL合成 `0x42ec00`。参数读取索引、字段写入和消费者已交叉核对。

证据：中心判据 `0x43a270`，setter的即时消费和合成调用 `0x432999–0x4329a9`、`0x432e45–0x432e5c`；tick `0x42e5a0`，敌更新 `0x42ff80`；限位 `0x42ec77–0x42ed2e`。

原生核验使用renkolab已有TH18 Ghidra工程：社区`labels.json`定位94到`0x48d0c8`；分派取opcode后经`0x48d3b8`/`0x48d2a8`跳转。Listing在`0x48d0c8–0x48d16c`读取phi/axis并算角差、极坐标，`0x48d171–0x48d1d8`缩放局部x并旋转，`0x48d1e8–0x48d206`写两输出。输入实际读取顺序为phi、axis、radius、ratio；本批local输入无随机副作用。极坐标helper为`0x48d900`，sin/cos包装为`0x404e10`/`0x404df0`。当前指令分支没有PosVel消费者的百分位floor。

原作依据为 renkolab 现有 `local/th18.v1.00a/state/data/functions.jsonl`：分派 `0x430d30`，Line initialize `0x4490d0` / tick `0x44a4f0`，Infinite initialize `0x44c870` / tick `0x44cae0`，Curve initialize `0x44ed70` / tick `0x44f450`。目标依据为 stg-engine `docs/ecl-lang/9-lasers.md`、`crates/stg-core/src/world/laser.rs`、`integrate.rs` 与 `collide.rs`；手册末尾以 TH06 为背景的统一宽度换算不得覆盖本表的 TH18 分段规则。EX 复制参数见[EX 表](../../transcribe/th18/ex-effects.md)与[原生比较报告](2026-11-05-th16-th18-ex-comparison.md)。

## movement.md：## 插值为什么是线性

## 插值为什么是线性

以EnemyData为基址，角槽在+0x3c8，速度槽在+0x3f8；槽+0x28为duration，+0x2c为mode。setter分别是`0x41f600`和`0x41f630`。

`moveRand`把角槽start/end都设为α、duration=60、mode=4；角本来就不变，mode4不影响这条恒值轨迹。速度槽start=1/end=0、duration=60，但`0x4336da`–`0x4336e1`设置mode时ECX仍指向**角槽**，未写速度槽mode。这个观测在Listing中成立，不能按合理猜想“修正”为给速度槽mode4。

本卡速度槽mode实际为0，依据是完整的短路径：

1. Enemy构造`0x42e1cc`–`0x42e1ee`清零Enemy+0x122c开始的0x5600字节，覆盖速度槽mode（Enemy+0x1650，即EnemyData+0x424）。
2. Boss公共入口与Boss1进入本卡前没有正时长moveVelTime/moveSpeedTime；Boss1只使用同一moveRand，仍不写该mode。
3. BossCard1的`moveVelTime(0,0,0,0)`只取消两槽duration：`0x4321f7`–`0x43220c`调用`0x41b790`，后者仅清槽+0x28；不能据第二实参0声称它重置了mode。

mode0在`0x402fb0`的普通曲线函数走默认`elapsed/duration`。`0x41f640`先递增elapsed，再计算值；第60次明确返回终值并清duration。于是后续运动tick k=1..60：

```text
speed(k) = 1 − k/60
α(k) = α
Δ(k) = speed(k) × (cos α, sin α)
```

未限位总位移为29.5像素；前30次为22.25。第60次速度0，此后停止，直到下一次moveRand重建槽。本卡在源t90首次配置，每165帧重复，所以下次配置前已停105帧。
