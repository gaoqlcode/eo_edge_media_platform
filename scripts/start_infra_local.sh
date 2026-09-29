#!/usr/bin/env bash
# 文件：scripts/start_infra_local.sh
# 内容：无 Docker/sudo 时，用 micromamba 环境启动本机 PostgreSQL + Redis
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MM="${ROOT}/.tools/bin/micromamba"
export MAMBA_ROOT_PREFIX="${ROOT}/.tools/mamba_root"
EMP_PREFIX="${MAMBA_ROOT_PREFIX}/envs/emp"
DATA_DIR="${ROOT}/.run/pgdata"
REDIS_DIR="${ROOT}/.run/redis"
PGPORT="${EMP_PGPORT:-55432}"
REDIS_PORT="${EMP_REDIS_PORT:-56379}"

mkdir -p "${ROOT}/.run" "${REDIS_DIR}"

if [[ ! -x "${MM}" ]]; then
  echo "缺少 micromamba: ${MM}"
  exit 1
fi

export PATH="${EMP_PREFIX}/bin:${PATH}"

# --- PostgreSQL ---
if [[ ! -f "${DATA_DIR}/PG_VERSION" ]]; then
  echo "[infra] initdb ..."
  initdb -D "${DATA_DIR}" --auth-local=trust --auth-host=trust --username=emp --encoding=UTF8
  # 监听端口
  {
    echo "listen_addresses = '127.0.0.1'"
    echo "port = ${PGPORT}"
    echo "unix_socket_directories = '${ROOT}/.run'"
  } >> "${DATA_DIR}/postgresql.conf"
fi

if ! pg_isready -h 127.0.0.1 -p "${PGPORT}" -U emp >/dev/null 2>&1; then
  echo "[infra] 启动 postgres :${PGPORT}"
  pg_ctl -D "${DATA_DIR}" -l "${ROOT}/.run/postgres.log" -o "-p ${PGPORT}" start
  sleep 1
fi

# 建库
createdb -h 127.0.0.1 -p "${PGPORT}" -U emp emp_platform 2>/dev/null || true
psql -h 127.0.0.1 -p "${PGPORT}" -U emp -d emp_platform -v ON_ERROR_STOP=1 \
  -f "${ROOT}/platform/infra/migrations/001_init_schema.sql"
psql -h 127.0.0.1 -p "${PGPORT}" -U emp -d emp_platform -v ON_ERROR_STOP=1 \
  -f "${ROOT}/platform/infra/migrations/002_seed_demo.sql"

# --- Redis ---
if ! redis-cli -p "${REDIS_PORT}" ping >/dev/null 2>&1; then
  echo "[infra] 启动 redis :${REDIS_PORT}"
  redis-server --port "${REDIS_PORT}" --dir "${REDIS_DIR}" --daemonize yes \
    --logfile "${ROOT}/.run/redis.log" --save "" --appendonly no
fi

echo "DATABASE_URL=postgresql+psycopg2://emp@127.0.0.1:${PGPORT}/emp_platform"
echo "REDIS_URL=redis://127.0.0.1:${REDIS_PORT}/0"
echo "[infra] OK"
