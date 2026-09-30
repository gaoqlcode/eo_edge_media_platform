"""单元测试：鉴权双模、幂等、指标"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "platform/libs/emp_py"))

os.environ["DATABASE_URL"] = "sqlite:////tmp/emp_unit.db"
os.environ["EMP_API_KEY"] = "emp-dev-key"
os.environ["EMP_JWT_SECRET"] = "unit-secret"
os.environ["EMP_MEMORY_BUS"] = "1"


def test_metrics_render():
    from emp_py.metrics import inc, render_prometheus

    inc("emp_test_counter")
    text = render_prometheus("unit")
    assert "emp_up" in text
    assert "emp_test_counter" in text


def test_api_key_reject():
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from emp_py.auth import require_api_key

    app = FastAPI()

    @app.get("/secure")
    def secure(_k: str = Depends(require_api_key)):
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/secure").status_code == 401
    assert client.get("/secure", headers={"X-API-Key": "emp-dev-key"}).status_code == 200


def test_dual_auth_jwt_and_key():
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from emp_py.auth import require_auth
    from emp_py.jwt_auth import issue_token

    app = FastAPI()

    @app.get("/secure")
    def secure(auth: dict = Depends(require_auth)):
        return auth

    client = TestClient(app)
    assert client.get("/secure").status_code == 401
    r = client.get("/secure", headers={"X-API-Key": "emp-dev-key"})
    assert r.status_code == 200 and r.json()["mode"] == "api_key"
    tok = issue_token("alice", role="admin")["access_token"]
    r2 = client.get("/secure", headers={"Authorization": f"Bearer {tok}"})
    assert r2.status_code == 200 and r2.json()["mode"] == "jwt"
    assert r2.json()["sub"] == "alice"


def test_device_token_and_rbac():
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from emp_py.auth import require_auth, require_roles
    from emp_py.jwt_auth import issue_token

    app = FastAPI()

    @app.get("/any")
    def any_auth(auth: dict = Depends(require_auth)):
        return auth

    @app.get("/admin-only")
    def admin_only(auth: dict = Depends(require_roles("admin", "service"))):
        return auth

    client = TestClient(app)
    assert client.get("/any", headers={"X-Device-Token": "emp-dev-key"}).status_code == 200
    assert client.get("/any", headers={"X-Device-Token": "emp-dev-key"}).json()["role"] == "device"
    # device 不能进 admin-only
    assert client.get("/admin-only", headers={"X-Device-Token": "emp-dev-key"}).status_code == 403
    assert client.get("/admin-only", headers={"X-API-Key": "emp-dev-key"}).status_code == 200
    tok = issue_token("bob", role="operator")["access_token"]
    assert client.get("/admin-only", headers={"Authorization": f"Bearer {tok}"}).status_code == 403


def test_idempotency():
    import uuid
    from emp_py.idempotency import already_processed

    eid = f"unit-idem-{uuid.uuid4().hex}"
    assert already_processed(eid) is False
    assert already_processed(eid) is True


def test_trace_extract():
    from emp_py.tracing import extract_or_create_trace_id, format_traceparent, span

    assert extract_or_create_trace_id("abc") == "abc"
    tid = extract_or_create_trace_id(None, "00-0123456789abcdef0123456789abcdef-0123456789abcdef-01")
    assert tid.startswith("0123456789abcdef")
    tp = format_traceparent("aabbccdd" * 4, "1122334455667788")
    assert tp.startswith("00-") and tp.endswith("-01")
    with span("unit") as sid:
        assert len(sid) == 16
