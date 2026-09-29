"""单元测试：鉴权与指标渲染（不依赖外部中间件）"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "platform/libs/emp_py"))

os.environ["DATABASE_URL"] = "sqlite:////tmp/emp_unit.db"
os.environ["EMP_API_KEY"] = "emp-dev-key"
os.environ["EMP_MEMORY_BUS"] = "1"


def test_metrics_render():
    from emp_py.metrics import inc, render_prometheus

    inc("emp_test_counter")
    text = render_prometheus("unit")
    assert "emp_up" in text
    assert "emp_test_counter" in text


def test_api_key_reject():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from emp_py.auth import require_api_key
    from fastapi import Depends

    app = FastAPI()

    @app.get("/secure")
    def secure(_k: str = Depends(require_api_key)):
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/secure").status_code == 401
    assert client.get("/secure", headers={"X-API-Key": "emp-dev-key"}).status_code == 200
