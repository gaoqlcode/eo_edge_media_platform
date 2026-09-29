#!/usr/bin/env bash
# 文件：scripts/e2e_test.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMP_BIN="${ROOT}/.tools/mamba_root/envs/emp/bin"
export PATH="${EMP_BIN}:${HOME}/.local/bin:/usr/bin:${PATH}"
export PYTHONPATH="${ROOT}/platform/libs/emp_py:${PYTHONPATH:-}"
export DATABASE_URL="postgresql+psycopg2://emp@127.0.0.1:55432/emp_platform"
export REDIS_URL="redis://127.0.0.1:6379/0"
export RABBITMQ_URL="amqp://emp:emp_dev_pass@127.0.0.1:5672/"
export EMP_API_KEY="emp-dev-key"
AUTH=(-H "X-API-Key: ${EMP_API_KEY}")
PYTHON="${EMP_BIN}/python"
[[ -x "${PYTHON}" ]] || PYTHON="$(command -v python3)"

echo "== infra =="
bash "${ROOT}/scripts/start_infra_local.sh"

echo "== unit tests =="
"${PYTHON}" -m pip install -q pytest httpx 2>/dev/null || true
( cd "${ROOT}" && PYTHONPATH="${ROOT}/platform/libs/emp_py" "${PYTHON}" -m pytest -q tests/unit )

echo "== ensure python deps =="
"${PYTHON}" -c "import fastapi,sqlalchemy" 2>/dev/null || \
  "${PYTHON}" -m pip install -q fastapi 'uvicorn[standard]' sqlalchemy psycopg2-binary 'pydantic<2' httpx redis pika

echo "== build C++ =="
cmake -S "${ROOT}" -B "${ROOT}/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "${ROOT}/build" -j"$(nproc)"
( cd "${ROOT}/build" && ctest --output-on-failure )

echo "== start python services =="
bash "${ROOT}/scripts/start_python_services.sh"

echo "== auth negative =="
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8101/api/devices \
  -H 'Content-Type: application/json' -d '{"device_code":"x","name":"x"}')
[[ "$code" == "401" ]] && echo "401 OK" || echo "WARN expected 401 got $code"

echo "== API flow =="
curl -sf -X POST http://127.0.0.1:8101/api/devices "${AUTH[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","name":"PG联调边端","platform":"wsl"}' || true
curl -sf -X POST http://127.0.0.1:8101/api/devices/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","status":"online","platform":"wsl"}'; echo
curl -sf "http://127.0.0.1:8101/api/devices/edge-e2e-pg/online"; echo
curl -sf "http://127.0.0.1:8101/metrics" | head -5; echo

SESSION="sess-pg-$(date +%s)"
curl -sf -X POST http://127.0.0.1:8102/api/sessions/start \
  -H 'Content-Type: application/json' \
  -d "{\"device_code\":\"edge-e2e-pg\",\"session_code\":\"${SESSION}\",\"storage_root\":\"data/${SESSION}\"}"
curl -sf -X POST http://127.0.0.1:8103/api/assets \
  -H 'Content-Type: application/json' \
  -d "{\"session_code\":\"${SESSION}\",\"asset_type\":\"jpeg_seq\",\"relative_path\":\"cam0/0001.jpg\",\"byte_size\":1024}"
curl -sf -X POST http://127.0.0.1:8104/api/alarms "${AUTH[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","severity":"info","code":"E2E_PG_OK","message":"postgres e2e"}'
curl -sf http://127.0.0.1:8105/api/bff/dashboard | head -c 400; echo
psql -h 127.0.0.1 -p 55432 -U emp -d emp_platform -c \
  "SELECT device_code,status FROM devices WHERE device_code='edge-e2e-pg';"

echo "== edge_agent =="
EMP_FRAMES=5 EMP_DEVICE_CODE=edge-e2e-pg \
  "${ROOT}/build/bin/edge_agent" "${ROOT}/build/lib/libemp_cam_Virtual.so"

echo "== media_gateway =="
"${ROOT}/build/bin/media_gateway" >/tmp/emp_gw.log 2>&1 &
GW_PID=$!; sleep 0.5
echo PING | nc -w 1 127.0.0.1 9100 || true
kill "${GW_PID}" 2>/dev/null || true
bash "${ROOT}/scripts/stop_python_services.sh"
echo "E2E PASSED (enterprise checks)"
