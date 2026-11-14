# stg-rl-train 项目指引

## 进入项目先读

- 主会话每次开始任务，先读 [项目记忆索引](docs/agent-memory/MEMORY.md)，再按任务打开相关条目；这些是跨会话保存的用户约定和项目经验。已由主会话准备并通过transcribe/run.py派发的固定单卡worker，按task.md、source.txt和随附的有关章节执行，不再读取整份项目记忆/实验历史或进行项目级规划；代码权限、已批准简化等约束仍须遵守。
- 项目是 stg-engine 躲弹模型的 PPO 训练仓，同时包含 TH06／TH16／TH18 弹幕转写与合成练习卡资料。
- 开发入口见 [README.md](README.md)；当前研究顺序见 [下一步](docs/next-steps.md)；训练设计见 [设计文档](docs/2026-09-15-stg-rl-train-design.md)；实验经过与结论见 [实验记录](docs/experiments.md)。
- Magnus 工作先读 [迁移说明](docs/magnus-migration.md)。TH06/NC 转写先读 [转写总览](transcribe/README.md)、[TH06 操作说明](transcribe/th06/README.md)、[转写设计](docs/2026-09-16-th06-transcribe-design.md) 和 `transcribe/th06/contracts/` 中对应阶段的约定；TH18主会话按[短skill](.claude/skills/th18-transcribe/SKILL.md)进入准备/维护流程；固定单卡worker只按注入的角色说明、task/source及任务给出的[TH18规则书](transcribe/th18/README.md)和引擎ECL手册执行，不重读skill、流程README或项目历史。单卡使用共用 validate 的 [TH18 规则](transcribe/th18/validation.md)，不沿用 TH06 批量切分/摘录命令。

## 用户约定

- 在 `main` 上工作，不自行创建功能分支或 worktree。用户明确要求提交才 commit，明确要求推送才 `git push origin main`；两项授权分开。不要把历史记忆中的操作命令当作当前执行请求。
- 主代理若为 Astra，大规模代码探索、修改与验证优先委派，类似任务优先 Sol／medium；主代理负责判断与审查，交接明确范围、文件责任和验收证据。简单记忆维护可直接完成。
- **当前研究状态（2026-11-15）**：扩池后的单层u4000／u6000与SA2 u4000及本机深度诊断已结束，用户要求阶段保存后再考虑模型优化。训练起点实际Hard504／Normal14／Extra150、无Lunatic；后续先区分训练难度与评测难度。结果和候选统一见[研究待办](docs/next-steps.md)，新架构、接口、训练配置及预算仍需用户确定。旧Perceiver方案／原型不构成恢复授权；不自动继续训练或替换部署模型。
- 研究方案优先改环境或引擎的真实机制。避免向观测塞入人为构造的几何答案，也不要用固定罚款式 reward 塑形代替真实后果；确需这样做时先说明理由并征求用户同意。
- 需要引擎接口时直接在 stg-engine 解决；修改前读取该仓库适用的 `AGENTS.md`，以及尚未迁移的 `CLAUDE.md`。保留原有引擎要求：P4 坏参数 no-op + 计数、写 API 钳制、`ENGINE_VER` bump 评审、golden 校验和对拍。
- 难度 rank 从 0 开始：`0 = Easy`、`1 = Normal`、`2 = Hard`、`3 = Lunatic`；`r2` 是 Hard，`r3` 是 Lunatic。

## 开发与验证

```bash
uv sync --frozen
uv run --frozen pytest -q
bash run.sh configs/smoke.toml smoke
```

- 根据改动运行相关测试。纯文档改动检查内容与链接即可；不要为了文档迁移启动训练。
- 本地依赖以 `pyproject.toml` / `uv.lock` 为准。迁移时（2026-09-26）本地为 Python 3.12、torch 2.14.0、tensordict 0.14.2；Magnus 的 `magnus/bootstrap.sh` 使用 Python 3.11、torch 2.5.1+cu124、tensordict 0.6.2。
- 修改 PPO、CUDA 图或 torch / tensordict API 后，提交 Magnus Job 前必须先在旧版本 CPU venv 跑相关测试；CUDA 图仍需实际 GPU 验证。准备方式见 [Magnus 版本兼容检查](docs/magnus-migration.md#旧-cpu-栈检查)。
- 升级 `stg_rl` 必须同步 `pyproject.toml`、`uv.lock`、`magnus/wheels/*.whl` 和 `magnus/wheels/SHA256SUMS`，核对哈希一致；引擎变化后同批重跑对照。

## 训练资源与长任务

- Magnus Job 一律显式 `--job-type B2`，不用 A2。提交前 `magnus cluster` 查看 `cpu_free` 和 GPU 空闲量，不默认申请 64 核；提交后几分钟检查状态。
- 租机的 `nproc` 和逐核占用可能是宿主机数据，不能当作实例配额。开跑前检查 cgroup 的 `cpu.max` / `cpu.stat`，并行训练按实际配额分线程。24 核租机、112 核 Magnus 节点是历史记录，换实例后重新确认。
- 环境变量放在 `taskset` / 命令前。后台启动后检查目标 Python 进程、CPU 占用和日志，不能只看到外层 shell 就报告“在跑”。监控同时处理结果完成和进程提前退出。
- 非交互执行已获授权的 `magnus job kill` 时需要 `-f`；该参数本身不构成终止任务的授权。

## 转写与产物

- 2026-11-09用户将下一作优先级改为[TH14](transcribe/th14/README.md)，沿用现代ECL流程：本作thdat／thecl及eclmap源准备、Priw8表对照已完成，同日三名Sol完成[一至七面静态切分](transcribe/th14/splitting.md)，后按用户确认合并道中并准备130份任务包。2026-11-11普通QoderCN及Sol作者阶段结束，具体交付、机器检查与搁置项见本作指南。同日按用户授权在renkolab建立 `local/th14.v1.00b/ghidra_projects/th14.exe.gpr` 并导入th-re-data，工具使用完整键 `th14.v1.00b`，登记在该仓 `games/th14.v1.00b/INDEX.md`。共有说明复用TH16／TH18，保留本作编号、弹型及回调差异，不把现代系列关系当作全部原生语义已核。[TH08准备材料](transcribe/th08/README.md)及已导入th-re-data的持久Ghidra保留，当前不优先推进；以后接续时按旧式sub/timeline和TH06经验，不套现代编号。原生调查先用社区已导入的命名、类型和标签，不跳过命名层裸读，不重新建库；源准备不授权自动启动作者、历史模型A/B或训练。

- TH15按[准备指南](transcribe/th15/README.md)接续，复用TH16/TH18共有语义和转写指南，不将逐项原生逆向作为前置要求。目标为合成训练数据，章节入口、状态及相关刷怪门控允许删除，仍按较短攻击切卡。funcSet专项已核：0清当前回调，1–4改变弹/激光行为；六个特殊攻击单列给Sol，不进入默认QoderCN批次。用户已允许无关音效省略、任务弹/公开API近似激光移动和邻近响应，不可行则跳过并记录；不扩引擎或实体池。2026-11-08用户决定阶段性结束TH15作者转写，验收状态及剩余项以本作指南为准。搁置段池阻塞 `th15_s3_b4`，暂缓 `th15_s2_b4`、`th15_s3_w04`、`th15_s5_b4`、`th15_s6_b4`、`th15_s6_b9`；保留报告/草稿，有元数据者设enabled=false，均移出默认派发/返工清单。未经用户重新决定，不继续调查、重派、审核收卡或启用，不扩池、减弹或缩寿命继续接纳；不把阶段收尾当作全批验收或训练授权。

- TH16按[本作指南](transcribe/th16/README.md)准备；用户已批准type0–43复用已核同值TH18槽，用本作TH16_*别名且source=th16，详见弹型专题。曲线激光相关攻击暂缓；六面SUBSEASON四种分别计四卡，不混成随机季节卡。

- **TH16明确不做（2026-11-08）**：用户决定排除 `th16_s3_w08`、`th16_s5_w04`、`th16_s5_w06`、`th16_s6_b8`；保留草稿并设 `enabled=false`，从默认派发/返工清单移除。不再为这四卡调查、扩池、减弹或改寿命；未经用户重新决定，不重派、审核收卡或启用。`th16_s4_w04`另按源修正每轮一发，继续保留。明细见[TH16总览](transcribe/th16/README.md#明确不做的攻击)。

- **明确训练取舍（2026-11-07）**：`th18_s6_w08` 排除出训练与默认派发，卡保留并设 `enabled=false`。原作依赖玩家主动击破敌人控制持续发射压力，与当前无敌敌人训练外壳不匹配；不通过扩池、减弹或缩短寿命继续接纳。xform段池保持2048；未经用户重新决定，不重派、收卡或启用此卡。`th18_s6_b10` 的既有暂缓另行保留。

- 新转写统一用[命令行流水线](transcribe/README.md)：清单直接填官方headless argv（如codex exec或dsh --profile headless），通过stdin交任务。不使用本机自制dsh-flash、MCP或DSH派发skill。作者直接写card，完整validate由执行器做一次。历史DSH审核后的Opus抽检及逐条复核约定保留，具体见[抽检要求](transcribe/README.md#既有批次的-opus-抽检)；不要把别的模型冒名为Opus。
- 成品按 `cards/<th06|th16|th18|synthetic>/<id>/` 放置，生产资料在 `transcribe/` 下同名目录；细分用metadata，暂停用 `enabled=false`，不再建根目录 `cards-*`。实验加载用 `configured_cards(cfg["env"])` 保留来源/标签筛选。
- 新转写/合成任务不重复加入hash、冻结或签名要求；保留必要编译运行与独立审核，行为变化只补受影响检查。历史SHA流程不默认推广，引擎wheel交付一致性约定另行保留。
- 已批准的简化连同其自然时序后果一起执行，写审不得以保真/稳妥为由补回省略机制或重新设为阻塞。TH18出生阶段整体省略后ACCEL等可立即开始，具体范围见 `transcribe/th18/transcription-policy.md`。
- `transcribe/work/` 含原作 ECL 摘录，永不入库；`runs/`、`dist/`、虚拟环境和构建产物遵守现有 `.gitignore`。
- TH06NC 部署侧保留用户要求的 8 帧激光运动平滑，不自行改成单帧；依据见 [T8 打包记录](docs/practice-cards/2026-10-02-t8-th06nc-package.md)。
- ONNX 导出后检查自动 torch / onnxruntime 对拍；改图签名时训练侧与部署侧一起更新 `GRAPH_VERSION`。细节见 README。

- **TH14阶段收尾（2026-11-11）**：按用户要求先完成Sol四个特殊项，再阶段性结束作者转写。普通121 written；Sol `th14_s6_b9`、`th14_s6_b10`、`th14_s7_b8` 完整机器检查通过，均待独立审核，未整批验收／收卡／训练。搁置 `th14_s2_w06`、`th14_s6_b4`、`th14_s6_b5`、`th14_s6_b6`、`th14_s6_b7`、`th14_s6_b8`，有元数据的草稿设enabled=false，移出默认派发／返工；原5待补、9暂缓维持排除。未经用户重新决定，不继续调查、重派、审核收卡或启用搁置项，不扩池、减弹或缩寿命；具体缺口、报告与验证范围见[TH14阶段记录](transcribe/th14/README.md)。

- TH14弹型按2026-11-09用户确认复用既有现代目录，使用[TH14词表](transcribe/th14/touhou-bullets.ecl)：原type0–23对应目标同号，24–42对应目标TH18 type加1；基础半径及色槽已核。属于合成映射，不宣称原始资源逐字节相同，不新增引擎槽或wheel。

- TH14特殊函数按[本作口径](transcribe/th14/special-functions.md)：用户已明确2号画面操作省略；3／4号保留真实玩家判定变化，已有 `set_player_hitbox` 可复用，无需重复加指令；1／5／6能用现有任务弹／signal合理表达就做，不能则允许跳过并记原因，不扩接口／池。1号缺少最近标记弹查询，暂按可跳过项；5号保留源标记边界，尤其不能为六面第六符补REACT使其触发；6号已有一次性signal配方。

## 维护项目记忆

- 本仓库用 `docs/agent-memory/` 保存可版本管理的记忆，由本文件要求读取；不要依赖 Claude 私有目录或假定这些 Markdown 会由 Codex 自动递归加载。
- 稳定工作约定集中在本文件；记忆只保留必要背景、证据位置与启动概况。实验结果、调查过程和批次进度写入对应项目文档，索引只链接入口，不逐轮摘录；已有资料能承载时不再新增记忆条目。
- 区分用户偏好、历史观察与当前事实。版本、资源、余额、运行状态和“未提交”等信息需核验，更新时注明日期和依据。
