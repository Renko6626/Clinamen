# 训练与诊断脚本

| 入口 | 用途 |
| --- | --- |
| [run.sh](../run.sh) | 安装锁定依赖，转交训练、续训、bench；另有probe模式 |
| [run-exp.sh](run-exp.sh) | 选环境线程，保存实际配置及控制台日志，再调用训练器 |
| [vast_profile.sh](../tools/vast_profile.sh) | 本轮真实PPO短测入口，详见[性能记录](../docs/perf-baseline.md) |
| [bench-step.py](bench-step.py)、[profile_update.py](profile_update.py) | 环境步与PPO更新诊断 |
| `diag/` | 历史模型、动作及推理间隔等专项分析 |

```bash
bash scripts/run-exp.sh configs/smoke.toml smoke --threads 2
```

`run-exp.sh` 依次采用显式 `--threads`、配置中正数 `env.threads`、bench推荐线程。换实例前先核对cgroup配额；不会根据宿主机型号／可见核心数套用旧线程数。实际配置写入 `runs/<名称>.toml`，日志写入 `runs/<名称>.console.log`。

旧L／O实验队列已移入[archive/run-night.sh](archive/run-night.sh)。它保留作历史资料，不再是当前夜间训练入口。当前配置见[配置说明](../configs/README.md)；本轮已确认从零4000次更新，实际启动状态见[实验记录](../docs/experiments.md)。
