"""
文件：control_bff/app.py — BFF 聚合；下游带 API Key
"""
import os
import sys
from pathlib import Path

import httpx
from fastapi import Depends
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.fastapi_app import create_service_app  # noqa: E402
from emp_py.jwt_auth import issue_token, require_jwt  # noqa: E402

app = create_service_app("control_bff")

DEVICE_URL = "http://127.0.0.1:8101"
SESSION_URL = "http://127.0.0.1:8102"
ALARM_URL = "http://127.0.0.1:8104"
API_KEY = os.getenv("EMP_API_KEY", "emp-dev-key")
ADMIN_USER = os.getenv("EMP_ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("EMP_ADMIN_PASS", "admin123")


class LoginIn(BaseModel):
    username: str
    password: str


@app.post("/api/bff/login")
def login(body: LoginIn):
    """教学用固定账号；生产接 LDAP/OIDC。"""
    if body.username != ADMIN_USER or body.password != ADMIN_PASS:
        from fastapi import HTTPException

        raise HTTPException(401, "bad credentials")
    return issue_token(body.username, role="admin")


@app.get("/api/bff/me")
def me(claims: dict = Depends(require_jwt)):
    return {"user": claims.get("sub"), "role": claims.get("role")}


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
