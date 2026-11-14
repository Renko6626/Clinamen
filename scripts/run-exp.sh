#!/usr/bin/env bash
# 上机跑一个实验：装依赖 → 选线程数 → 训练（结束自动评测、出图、打包）。
#
#   bash scripts/run-exp.sh configs/smoke.toml smoke
#   bash scripts/run-exp.sh configs/smoke.toml smoke --threads 2
#
# 线程数：显式 --threads → 配置 env.threads → --bench 推荐值。
# 换机器先核对 cgroup 配额；配置中的线程数不会自动适配新实例。
# 选定值写进 runs/<名>.toml，源配置保留。
# 终端输出同时写 runs/<名>.console.log。建议在 tmux 里跑。
set -euo pipefail
cd "$(dirname "$0")/.."

[[ $# -ge 2 ]] || { echo "用法：bash scripts/run-exp.sh <配置> <运行名> [--threads N]" >&2; exit 2; }
CFG=$1; NAME=$2; shift 2
THREADS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --threads) [[ $# -ge 2 ]] || { echo "--threads 缺少线程数" >&2; exit 2; }; THREADS="$2"; shift 2 ;;
    *) echo "未知参数 $1" >&2; exit 2 ;;
  esac
done
if [[ -n "$THREADS" && ! "$THREADS" =~ ^[1-9][0-9]*$ ]]; then
  echo "--threads 须为正整数" >&2; exit 2
fi

export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --frozen
mkdir -p runs

if [[ -z "$THREADS" ]]; then
  THREADS="$(uv run --frozen python - "$CFG" <<'PY'
import sys
from stgtrain.config import load_config
print(load_config(sys.argv[1])["env"]["threads"])
PY
)"
  if [[ "$THREADS" -gt 0 ]]; then
    echo "使用配置 env.threads = $THREADS"
  else
    echo "配置未指定正线程数，先跑 bench 选线程……"
    uv run --frozen python -m stgtrain.train "$CFG" "$NAME" --bench
    BENCH="$(ls -td runs/*bench-"$NAME"*/ | head -1)"
    THREADS="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['recommended']['threads'])" "$BENCH/bench.json")"
    echo "bench 推荐 threads = $THREADS（$BENCH/bench.json）"
  fi
fi

RUN_CFG="runs/$NAME.toml"
uv run --frozen python - "$CFG" "$RUN_CFG" "$THREADS" <<'PY'
import sys
from stgtrain.config import dump_toml, load_config
source, destination, threads = sys.argv[1:]
dump_toml(load_config(source, {"env": {"threads": int(threads)}}), destination)
PY
echo "配置副本：$RUN_CFG（仓库 $(git rev-parse --short HEAD)）"
uv run --frozen python -m stgtrain.train "$RUN_CFG" "$NAME" 2>&1 | tee "runs/$NAME.console.log"
