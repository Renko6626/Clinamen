# Magnus备用训练入口

本阶段优先Vast.ai；Magnus保留已有备用路线，不更换软件栈。完整限制与提交参数见[迁移说明](../docs/magnus-migration.md)，资源操作约定见[项目规则](../AGENTS.md)。

| 文件 | 用途 |
| --- | --- |
| [train.sh](train.sh) | 单条训练，已有结果打包交回 |
| [train-multi.sh](train-multi.sh) | 同Job多条训练，线程按实际资源分配 |
| [smoke.sh](smoke.sh)、[bench.sh](bench.sh) | 环境冒烟与吞吐检查 |
| [bootstrap.sh](bootstrap.sh)、[lib.sh](lib.sh) | 现有依赖安装与结果交回共用逻辑 |
| `wheels/` | 本地／Magnus共用引擎wheel，位置保持不变 |

Python3.11、torch2.5.1+cu124、tensordict0.6.2仍由bootstrap安装；不可用本地锁定栈替代后宣称完成兼容验证。退出时会尝试交回结果，人工强杀前仍须考虑工作区清理的限制。

八个历史实验与性能探针脚本已移入[archive](archive/README.md)，当前通用入口不依赖它们。
