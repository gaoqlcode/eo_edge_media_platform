#!/usr/bin/env bash
# 文件：scripts/stop_infra_local.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export MAMBA_ROOT_PREFIX="${ROOT}/.tools/mamba_root"
export PATH="${MAMBA_ROOT_PREFIX}/envs/emp/bin:${PATH}"
PGPORT="${EMP_PGPORT:-55432}"
REDIS_PORT="${EMP_REDIS_PORT:-56379}"
DATA_DIR="${ROOT}/.run/pgdata"

if [[ -d "${DATA_DIR}" ]]; then
  pg_ctl -D "${DATA_DIR}" stop -m fast 2>/dev/null || true
fi
redis-cli -p "${REDIS_PORT}" shutdown 2>/dev/null || true
echo "infra stopped"
