# TH16 一面试运行的三处问题核查

2026-11-07。仅针对QoderCN/dfmodel一面12张作者产物中报告的FINAL_ANGLE、floatTime参数序、b3时限；不代表整批独立语义审核。版本为TH16 v1.00a。

## 结论与改动

| 项目 | 核查结论 | 处理 |
|---|---|---|
| w04的FINAL_ANGLE | 来自最终位置本帧位移，包含ABS/REL合成；不能仅取ABS_ANGLE | 本次疑问解除，保留该卡代码；补明确的变量说明 |
| b1–b4的floatTime | 教材签名正确；原始二进制第三参为0，第四参600/1200。原生立即写start，时长0不再帧末推进 | 删除作者自行加入的线性渐密，改为源初值对应的固定间隔 |
| b3的时限 | 源1500帧含自身90+30帧等待，活动发射1380帧；外壳120帧另算 | 恢复源90+30帧等待，TIME_LIMIT/meta改回1624，仍保留1380帧活动窗口 |

四张的随机偏移发射支线等待间隔（E/N/H/L）：b1与b2为60/60/30/30帧，b3与b4为60/60/30/20帧。b4 Easy仍执行两次wait，因此实际波间隔为120帧。b3原实现Hard也误取20，本次按源30修正。

这里只修改工作区b1–b4的main.ecl及b3的meta；w04代码未动。原作者卡及报告保存在[修正前副本](../../transcribe/work/th16/stage1-issues/before/)，当前报告注明主会话修正。

## FINAL_ANGLE的证据

复用renkolab已有TH16原生导出，并对当前exe反汇编复核；未新建或改写Ghidra工程。

- `EnemyData::step_interpolators`（`0x41bb50`）先保存旧位置，再更新ABS/REL，调用`EnemyData::update_final_pos`（`0x41c1f0`）。其参数基址为enemy+`0x120c`。
- `update_final_pos`把新ABS/REL位置之和减旧final位置，写入data+`0x78/0x7c`，即enemy+`0x1284/0x1288`。
- 特殊变量读取器`0x424110`的−9958分支在`0x424544`把上述dx/dy装入XMM1/XMM0，调用`0x4052a0`的atan2；因此是合成位移方向。
- [Priw8变量表](https://priw8.github.io/js/ecl/vars.js)将−9958称为最终移动角，与原生链一致，但仅凭这个短描述不足以区分ABS与合成方向。

w04的`arm_step`已显式合成ABS速度和REL椭圆偏移的差值，再取atan2；本次对这一语义的疑问解除，不将本结论扩为对该卡全部运动时序的验收。

## floatTime的证据

[Priw8指令数据](https://priw8.github.io/js/ecl/ins.js)公共91签名为slot,var,time,mode,init,final；TH16教材沿用此顺序正确。

独立解析`st01bs.ecl`原始指令头及六个参数，四处opcode91为：

| sub | 文件偏移 | frames | mode |
|---|---:|---:|---:|
| Boss1_at2 | `0x0d90` | 0 | 1200 |
| Boss2_at2 | `0x1950` | 0 | 1200 |
| BossCard1_at2 | `0x2520` | 0 | 600 |
| BossCard2_at2 | `0x3524` | 0 | 1200 |

参数mask为`0x32`，第三/四参都是字面整数，不受栈取值影响。`thecl -r -d 16`的独立原始输出也保持0,600/1200，排除了高层反编译重排的解释。

原生`EclRunContext::ecl_run`（`0x472030`）opcode91分支：`0x4736fd`取索引2写插值器end_time；`0x47370c`起取索引3写method；`0x473766`取得out左值并立即写入start。帧末`0x4739b6`检查end_time，等于0则跳过该槽的推进及写回。故这些调用的out保持start，不应把600/1200解释为线性插值时长。暂不判断原作者写法的意图，转写保留可观察的实际行为。

原始字节、反汇编及来源副本见[本机证据目录](../../transcribe/work/th16/stage1-issues/)，关键参数见[opcode91-binary.json](../../transcribe/work/th16/stage1-issues/opcode91-binary.json)。

## b3的时限与验证

源Boss2在188行timerReset、210行setInterrupt(1500)之后，214/217行显式等待90+30帧，219/222行才启动发射。外壳约定是在120帧缓冲后执行源入口；它与源内等待分别保留。因此目标预算为120+1500+4=1624。修正只推迟整段源行为并保持源窗口，不延长活动发射时间。


四卡最终完整检查通过，各档诊断0；主会话只核本节列出的参数和时序问题，未完成整批独立语义审核、原作动态对拍或训练。当前卡状态以本作指南及metadata为准。
