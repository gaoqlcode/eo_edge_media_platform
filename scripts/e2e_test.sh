#!/usr/bin/env bash
# 文件：scripts/e2e_test.sh
# 内容：端到端验收：健康检查 → 心跳 → 会话 → 资产 → 告警 → BFF → C++ labs/edge
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export DATABASE_URL="${DATABASE_URL:-sqlite:////tmp/emp_platform.db}"
export PYTHONPATH="${ROOT}/platform/libs/emp_py:${PYTHONPATH:-}"

echo "== build C++ =="
cmake -S "${ROOT}" -B "${ROOT}/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "${ROOT}/build" -j"$(nproc)"
( cd "${ROOT}/build" && ctest --output-on-failure )

echo "== start python services =="
bash "${ROOT}/scripts/start_python_services.sh"

echo "== API flow =="
curl -sf -X POST http://127.0.0.1:8101/api/devices \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-sim-001","name":"模拟边端","platform":"wsl"}' || true

curl -sf -X POST http://127.0.0.1:8101/api/devices/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-sim-001","status":"online","platform":"wsl"}'

SESSION="sess-$(date +%s)"
curl -sf -X POST http://127.0.0.1:8102/api/sessions/start \
  -H 'Content-Type: application/json' \
  -d "{\"device_code\":\"edge-sim-001\",\"session_code\":\"${SESSION}\",\"storage_root\":\"data/${SESSION}\"}"

curl -sf -X POST http://127.0.0.1:8103/api/assets \
  -H 'Content-Type: application/json' \
  -d "{\"session_code\":\"${SESSION}\",\"asset_type\":\"jpeg_seq\",\"relative_path\":\"cam0/0001.jpg\",\"byte_size\":1024}"

curl -sf -X POST http://127.0.0.1:8104/api/alarms \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-sim-001","severity":"info","code":"E2E_OK","message":"e2e alarm"}'

curl -sf http://127.0.0.1:8105/api/bff/dashboard | head -c 400
echo

echo "== edge_agent (few frames) =="
EMP_FRAMES=5 EMP_DEVICE_CODE=edge-sim-001 \
  "${ROOT}/build/bin/edge_agent" "${ROOT}/build/lib/libemp_cam_Virtual.so"

echo "== media_gateway smoke =="
"${ROOT}/build/bin/media_gateway" >/tmp/emp_gw.log 2>&1 &
GW_PID=$!
sleep 0.5
echo PING | nc -w 1 127.0.0.1 9100 || true
echo "REGISTER ${SESSION} edge-sim-001" | nc -w 1 127.0.0.1 9100 || true
echo LIST | nc -w 1 127.0.0.1 9100 || true
kill "${GW_PID}" 2>/dev/null || true

bash "${ROOT}/scripts/stop_python_services.sh"
echo "E2E PASSED"
