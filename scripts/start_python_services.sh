#!/usr/bin/env bash
# 文件：scripts/start_python_services.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMP_BIN="${ROOT}/.tools/mamba_root/envs/emp/bin"
if [[ -x "${EMP_BIN}/python" ]]; then
  PYTHON="${EMP_BIN}/python"
  export PATH="${EMP_BIN}:${HOME}/.local/bin:${PATH}"
else
  PYTHON="$(command -v python3)"
  export PATH="${HOME}/.local/bin:${PATH}"
fi
export PYTHONPATH="${ROOT}/platform/libs/emp_py:${PYTHONPATH:-}"
# 默认强制本机 micromamba PostgreSQL（可用 EMP_DATABASE_URL 覆盖）
# 注意：不要沿用 shell 里残留的 sqlite DATABASE_URL
if [[ -n "${EMP_DATABASE_URL:-}" ]]; then
  export DATABASE_URL="${EMP_DATABASE_URL}"
elif [[ "${EMP_USE_SQLITE:-0}" == "1" ]]; then
  export DATABASE_URL="sqlite:////tmp/emp_platform.db"
else
  export DATABASE_URL="postgresql+psycopg2://emp@127.0.0.1:55432/emp_platform"
fi
export REDIS_URL="${EMP_REDIS_URL:-redis://127.0.0.1:6379/0}"
export RABBITMQ_URL="${EMP_RABBITMQ_URL:-amqp://emp:emp_dev_pass@127.0.0.1:5672/}"
export EMP_MEMORY_BUS="${EMP_MEMORY_BUS:-0}"

mkdir -p "${ROOT}/.run"
pkill -f "uvicorn app:app" 2>/dev/null || true
sleep 1

"${PYTHON}" -c "from emp_py.db import init_db; init_db(); print('db init ok')"

start_one() {
  local name="$1" port="$2" dir="$3"
  echo "[start] ${name} :${port}"
  (
    cd "${ROOT}/platform/services/${dir}"
    nohup "${PYTHON}" -m uvicorn app:app --host 127.0.0.1 --port "${port}" \
      >"${ROOT}/.run/${name}.log" 2>&1 &
    echo $! >"${ROOT}/.run/${name}.pid"
  )
  sleep 0.8
}

start_one device_service 8101 device_service
start_one session_service 8102 session_service
start_one media_indexer 8103 media_indexer
start_one alarm_service 8104 alarm_service
start_one control_bff 8105 control_bff

sleep 2
fail=0
for p in 8101 8102 8103 8104 8105; do
  if curl -sf "http://127.0.0.1:${p}/health"; then
    echo " port ${p} OK"
  else
    echo " port ${p} FAIL"; fail=1
  fi
done
echo "PYTHON=${PYTHON}"
echo "DATABASE_URL=${DATABASE_URL}"
exit "${fail}"
