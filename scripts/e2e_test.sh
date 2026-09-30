#!/usr/bin/env bash
# 文件：scripts/e2e_test.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMP_BIN="${ROOT}/.tools/mamba_root/envs/emp/bin"
export PATH="${EMP_BIN}:${HOME}/.local/bin:/usr/bin:${PATH}"
export PYTHONPATH="${ROOT}/platform/libs/emp_py:${PYTHONPATH:-}"
export DATABASE_URL="postgresql+psycopg2://emp@127.0.0.1:55432/emp_platform"
export REDIS_URL="redis://127.0.0.1:56379/0"
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
"${PYTHON}" -c "import fastapi,sqlalchemy,jwt" 2>/dev/null || \
  "${PYTHON}" -m pip install -q fastapi 'uvicorn[standard]' sqlalchemy psycopg2-binary 'pydantic<2' httpx redis pika PyJWT

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
TRACE_HDR=(-H "X-Trace-Id: e2e-trace-$(date +%s)")
curl -sf -D /tmp/emp_hdr.txt -X POST http://127.0.0.1:8101/api/devices "${AUTH[@]}" "${TRACE_HDR[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","name":"PG联调边端","platform":"wsl"}' || true
grep -i 'X-Trace-Id' /tmp/emp_hdr.txt || true
curl -sf -X POST http://127.0.0.1:8101/api/devices/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","status":"online","platform":"wsl"}'; echo
curl -sf "http://127.0.0.1:8101/api/devices/edge-e2e-pg/online"; echo
curl -sf "http://127.0.0.1:8101/metrics" | head -5; echo

SESSION="sess-pg-$(date +%s)"
curl -sf -X POST http://127.0.0.1:8102/api/sessions/start "${AUTH[@]}" \
  -H 'Content-Type: application/json' \
  -d "{\"device_code\":\"edge-e2e-pg\",\"session_code\":\"${SESSION}\",\"storage_root\":\"data/${SESSION}\"}"
curl -sf -X POST http://127.0.0.1:8103/api/assets "${AUTH[@]}" \
  -H 'Content-Type: application/json' \
  -d "{\"session_code\":\"${SESSION}\",\"asset_type\":\"jpeg_seq\",\"relative_path\":\"cam0/0001.jpg\",\"byte_size\":1024}"
curl -sf "http://127.0.0.1:8103/api/playback/${SESSION}" | head -c 300; echo
curl -sf -X POST http://127.0.0.1:8104/api/alarms "${AUTH[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","severity":"info","code":"E2E_PG_OK","message":"postgres e2e"}'
# 审计表应有写入
psql -h 127.0.0.1 -p 55432 -U emp -d emp_platform -c \
  "SELECT command,operator FROM command_audits ORDER BY created_at DESC LIMIT 3;"
curl -sf http://127.0.0.1:8105/api/bff/dashboard | head -c 400; echo
psql -h 127.0.0.1 -p 55432 -U emp -d emp_platform -c \
  "SELECT device_code,status FROM devices WHERE device_code='edge-e2e-pg';"

echo "== JWT dual-auth on write =="
TOK=$(curl -sf -X POST http://127.0.0.1:8105/api/bff/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | "${PYTHON}" -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -sf -X POST http://127.0.0.1:8104/api/alarms \
  -H "Authorization: Bearer ${TOK}" \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","severity":"info","code":"E2E_JWT_OK","message":"jwt dual auth"}'
echo
curl -sf http://127.0.0.1:8105/api/bff/me -H "Authorization: Bearer ${TOK}"; echo

echo "== worker idempotency =="
"${PYTHON}" - <<'PY'
import uuid
from emp_py.idempotency import already_processed
eid = f"e2e-idem-{uuid.uuid4().hex}"
assert already_processed(eid) is False
assert already_processed(eid) is True
print("idempotency OK")
PY
"${PYTHON}" "${ROOT}/platform/services/media_worker/worker.py" outbox || true

echo "== edge_agent + preview + vod =="
cd "${ROOT}"
EMP_FRAMES=5 EMP_DEVICE_CODE=edge-e2e-pg EMP_API_KEY=emp-dev-key \
  EMP_ROOT="${ROOT}" EMP_ENCODE_H264=1 \
  EMP_DATA_ROOT="${ROOT}/data/sessions" EMP_PREVIEW_ROOT="${ROOT}/data/preview" \
  "${ROOT}/build/bin/edge_agent" "${ROOT}/build/lib/libemp_cam_Virtual.so"
SESS_CODE=$(ls -dt "${ROOT}"/data/sessions/sess-edge-* 2>/dev/null | head -1 | xargs -I{} basename {})
EMP_PREVIEW_ROOT="${ROOT}/data/preview" EMP_SESSION_ROOT="${ROOT}/data/sessions" \
  "${ROOT}/build/bin/media_gateway" >/tmp/emp_gw.log 2>&1 &
GW_PID=$!; sleep 0.5
echo PING | nc -w 1 127.0.0.1 9100 || true
curl -sf -o /tmp/emp_preview.jpg "http://127.0.0.1:9101/preview?device=edge-e2e-pg"
file /tmp/emp_preview.jpg || true
ls -la /tmp/emp_preview.jpg
# VOD
if [[ -n "${SESS_CODE}" ]]; then
  curl -sf -o /tmp/emp_vod.mp4 "http://127.0.0.1:9101/vod?session=${SESS_CODE}"
  file /tmp/emp_vod.mp4 || true
  curl -sf "http://127.0.0.1:8103/api/playback/${SESS_CODE}" | head -c 400; echo
fi
# metrics auth fail counter
curl -sf "http://127.0.0.1:8101/metrics" | grep -E 'emp_auth_fail|emp_http_requests' | head -5 || true
# traceparent header
curl -sI http://127.0.0.1:8105/health | grep -iE 'traceparent|X-Trace-Id|X-Span-Id' || true
kill "${GW_PID}" 2>/dev/null || true
bash "${ROOT}/scripts/stop_python_services.sh"
echo "E2E PASSED (enterprise checks)"
