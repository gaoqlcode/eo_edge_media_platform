#!/usr/bin/env bash
# 文件：scripts/start_python_services.sh
# 内容：启动全部 Python 微服务（后台）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="${HOME}/.local/bin:${PATH}"
export PYTHONPATH="${ROOT}/platform/libs/emp_py:${PYTHONPATH:-}"
export DATABASE_URL="${DATABASE_URL:-sqlite:////tmp/emp_platform.db}"
export EMP_MEMORY_BUS=1

mkdir -p "${ROOT}/.run"

# 停旧进程
pkill -f "uvicorn app:app" 2>/dev/null || true
sleep 1

# 单次初始化库表，避免多服务并发 create_all 竞态
rm -f /tmp/emp_platform.db
python3 -c "from emp_py.db import init_db; init_db(); print('db init ok')"

start_one() {
  local name="$1" port="$2" dir="$3"
  echo "[start] ${name} :${port}"
  (
    cd "${ROOT}/platform/services/${dir}"
    nohup python3 -m uvicorn app:app --host 127.0.0.1 --port "${port}" \
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
    echo " port ${p} FAIL"
    fail=1
  fi
done
echo "logs: ${ROOT}/.run/*.log"
exit "${fail}"
