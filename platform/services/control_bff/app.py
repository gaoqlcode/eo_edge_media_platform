"""
文件：control_bff/app.py — BFF 聚合；下游带 API Key
"""
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.fastapi_app import create_service_app  # noqa: E402

app = create_service_app("control_bff")

DEVICE_URL = "http://127.0.0.1:8101"
SESSION_URL = "http://127.0.0.1:8102"
ALARM_URL = "http://127.0.0.1:8104"
API_KEY = os.getenv("EMP_API_KEY", "emp-dev-key")


@app.get("/api/bff/dashboard")
def dashboard():
    headers = {"X-API-Key": API_KEY}
    out = {"devices": [], "sessions": [], "alarms": [], "errors": []}
    with httpx.Client(timeout=2.0) as client:
        for key, url, need_key in (
            ("devices", f"{DEVICE_URL}/api/devices", False),
            ("sessions", f"{SESSION_URL}/api/sessions", True),
            ("alarms", f"{ALARM_URL}/api/alarms", False),
        ):
            try:
                h = headers if need_key else {}
                r = client.get(url, headers=h)
                r.raise_for_status()
                out[key] = r.json()
            except Exception as e:
                out["errors"].append({"source": key, "error": str(e)})
    return out
