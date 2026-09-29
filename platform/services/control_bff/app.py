"""
文件：control_bff/app.py
内容：BFF 聚合层 — 汇总设备/会话/告警，供客户端一次拉取
"""
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI

app = FastAPI(title="EMP control_bff", version="0.1.0")

DEVICE_URL = "http://127.0.0.1:8101"
SESSION_URL = "http://127.0.0.1:8102"
ALARM_URL = "http://127.0.0.1:8104"


@app.get("/health")
def health():
    return {"service": "control_bff", "status": "ok"}


@app.get("/api/bff/dashboard")
def dashboard():
    """聚合仪表盘数据；下游不可达时返回部分结果与错误字段。"""
    out = {"devices": [], "sessions": [], "alarms": [], "errors": []}
    with httpx.Client(timeout=2.0) as client:
        for key, url in (
            ("devices", f"{DEVICE_URL}/api/devices"),
            ("sessions", f"{SESSION_URL}/api/sessions"),
            ("alarms", f"{ALARM_URL}/api/alarms"),
        ):
            try:
                r = client.get(url)
                r.raise_for_status()
                out[key] = r.json()
            except Exception as e:
                out["errors"].append({"source": key, "error": str(e)})
    return out
