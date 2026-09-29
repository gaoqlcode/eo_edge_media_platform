#!/usr/bin/env bash
# 文件：scripts/stop_python_services.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -d "${ROOT}/.run" ]]; then
  for f in "${ROOT}"/.run/*.pid; do
    [[ -f "$f" ]] || continue
    kill "$(cat "$f")" 2>/dev/null || true
    rm -f "$f"
  done
fi
pkill -f "uvicorn .*app:app" 2>/dev/null || true
echo "stopped"
