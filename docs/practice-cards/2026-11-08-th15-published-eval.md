# TH15 发布模型试测（2026-11-08）

使用最近游戏包的 B/Shift K8 u1000 graph7 ONNX，对本轮129个已交付攻击各跑10局。共1290局，存活334局，胜率 **25.89%**；956局死亡、0超时、0执行错误。61段为0/10、5段为10/10，其余63段介于两者之间。

后续[关闭运动层对照](2026-11-08-th15-motor-off.md)用相同129段和种子得到438/1290（33.95%），提高8.06个百分点；本页保留原运动层基线结果。

## 结果与产物

| 关卡 | 段数 | 存活／局数 | 胜率 |
| --- | ---: | ---: | ---: |
| Stage1 | 16 | 64 / 160 | 40.00% |
| Stage2 | 15 | 53 / 150 | 35.33% |
| Stage3 | 16 | 39 / 160 | 24.38% |
| Stage4 | 18 | 32 / 180 | 17.78% |
| Stage5 | 18 | 32 / 180 | 17.78% |
| Stage6 | 14 | 21 / 140 | 15.00% |
| Extra | 32 | 93 / 320 | 29.06% |
| 合计 | 129 | 334 / 1290 | 25.89% |

- [逐段CSV](../../runs/th15-published-eval-20261108/summary.csv)：每段rank、胜率、死亡／超时、平均存活帧及静止检查状态。
- [汇总JSON](../../runs/th15-published-eval-20261108/summary.json)：分关结果、0/10及10/10的完整ID清单、观测截断记录。
- [逐局结果](../../runs/th15-published-eval-20261108/results.json)：每段10个环境的首次结束码与帧数。
- [启动参数](../../runs/th15-published-eval-20261108/launch.json)、[实际配置](../../runs/th15-published-eval-20261108/full-0/manifest.json)、[129段输入清单](../../runs/th15-published-eval-20261108/tasks.json)、[产物核验](../../runs/th15-published-eval-20261108/artifact-validation.json)。

原始结果、运行脚本及日志保留在被忽略的 `runs/th15-published-eval-20261108/`。8个分片均已结束，最慢分片536.8秒；本轮没有生成GIF或进行额外推理耗时基准。

## 模型与评测口径

模型来自 `dist/th06nc-ai-20261028-r2.zip` 的 `model.onnx`，已核对与 `dist/b-request-light-shift-k8-b2048-best.onnx` 逐字节相同。发布记录为 `dist/th06nc-ai-20261028-r2.release.json`，对应 B/Shift K8 的 update1000、262144000 env steps；未使用较新的未发布实验权重。

本次直接调用发布ONNX做策略推理，没有用当前Python网络实现代替发布图。checkpoint只提供原配置；图内特征与网络采用 danger_topk_v8 / set_attn_v3，输入为2048行子弹、256行敌人、64行激光，子弹Top-K64、激光Top-K8。

- 正篇97段取最高可用rank3（Lunatic），Extra32段取rank4；不混入低难度或已搁置的6项。
- 每段10个独立环境，基础seed12345，只记录各环境第一次结束。贪心FP32、每帧决策，自由躲弹，保留原训练运动层；不镜像、不增加判定半径；生产动作表固定含SHOT、不按炸弹，无敌外壳不靠玩家DPS推进。
- 环境与动作推进复用生产 `EnvWrapper`、运动层和 native `stg_rl`。每卡最大帧数为meta时限+300，避免旧checkpoint的统一帧数上限截断长卡。
- 胜利定义为引擎结束码2，即存活到段结束；结束码1为死亡、3为超时。已结束环境的自动重开局不进入分母。
- 8个CPU进程，每进程Torch／ORT／环境1线程；本次cgroup CPU配额不限。运行时stg_rl0.4.7 / ENGINE_VER35，ORT1.30.0。

## 诊断与解释边界

129段另以seed1、最高难度运行现有harness至时限+300，均退出0，task_faults、contract_viol、pool_full、hits_ovf、events_ovf、reqs_dropped六类诊断均为0。这是静止自机检查，不等于全部AI控制轨迹的池诊断，也不替代所有难度的完整机器验收。

`th15_s7_b11` 的首次AI轨迹中，累计216个环境帧出现子弹观测截断，累计丢弃8570行；发布图原始子弹输入上限为2048行。该段为0/10，容量现象不能单独证明死亡原因。此次仅统计子弹截断，没有量化激光观测丢失。

本轮评测的是尚未全部验收、独立审核的[TH15转写工作稿](../../transcribe/th15/README.md)，包含已批准合成取舍和无敌外壳。每段仅10局，用于粗筛模型表现，不能据此给原作攻击或人类难度排名。评测没有修改攻击、模型、引擎、正式插件或训练配置，没有恢复6个搁置项，没有收卡或启动训练。

## 核验

8路实际执行 `run_eval.py --shards 8 --shard <0..7>`，argv与进程记录见launch.json；`uv run --frozen python runs/th15-published-eval-20261108/finish.py` 成功聚合。产物检查确认129个唯一ID与本轮交付清单一致，每段10条首次局记录、全部1290条结束码合法，逐段／分关／整体分子分母一致，6个搁置ID未混入。当前卡result状态仍为128 written、1 validated，试测未将全批升级为审核通过或正式收卡。
