#!/usr/bin/env bash
# Extract the bundle, then: bash tools/vast_profile.sh --quota 32 --hourly 0.392
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p runs
finish() {
    status=$?
    trap - EXIT
    if [[ -d runs/benchmark ]]; then
        result_files=(benchmark)
        [[ ! -f runs/bootstrap-seconds ]] || result_files+=(bootstrap-seconds)
        [[ ! -d runs/failed-attempts ]] || result_files+=(failed-attempts)
        tar -czf runs/vast-profile-results.tar.gz -C runs "${result_files[@]}" || status=1
    fi
    printf '%s\n' "$status" > runs/profile-exit-code
    exit "$status"
}
trap finish EXIT
start_epoch=$(date +%s)
if ! command -v git >/dev/null || ! command -v cc >/dev/null || [[ ! -f /usr/include/python3.12/Python.h ]]; then
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git build-essential python3.12-dev ca-certificates curl
fi
if ! command -v uv >/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
uv sync --frozen --no-dev
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 TORCHINDUCTOR_COMPILE_THREADS=2
export PYTHONUNBUFFERED=1 MPLBACKEND=Agg
printf '%s\n' "$(( $(date +%s) - start_epoch ))" > runs/bootstrap-seconds
uv run --frozen --no-dev python -u tools/vast_profile.py suite --out runs/benchmark "$@"
