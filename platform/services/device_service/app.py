"""
文件：device_service/app.py
内容：设备微服务 — 注册/列表/心跳更新
"""
import sys
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 把公共库加入路径（开发态；安装包后可去掉）
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.db import get_db, init_db  # noqa: E402
from emp_py.models import Device, Tenant  # noqa: E402

app = FastAPI(title="EMP device_service", version="0.1.0")


class DeviceCreate(BaseModel):
    device_code: str
    name: str
    platform: str = "wsl"
    device_type: str = "edge"


class HeartbeatIn(BaseModel):
    device_code: str
    status: str = "online"
    platform: str = "wsl"


@app.on_event("startup")
def on_startup():
    init_db()
    db = next(get_db())
    try:
        t = db.query(Tenant).filter_by(code="default").first()
        if not t:
            t = Tenant(code="default", name="默认学习租户")
            db.add(t)
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"service": "device_service", "status": "ok"}


@app.get("/api/devices")
def list_devices(db: Session = Depends(get_db)):
    rows = db.query(Device).all()
    return [
        {
            "id": d.id,
            "device_code": d.device_code,
            "name": d.name,
            "status": d.status,
            "platform": d.platform,
            "last_seen_at": d.last_seen_at.isoformat() if d.last_seen_at else None,
        }
        for d in rows
    ]


@app.post("/api/devices")
def create_device(body: DeviceCreate, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter_by(code="default").first()
    if not tenant:
        raise HTTPException(500, "missing default tenant")
    exists = (
        db.query(Device)
        .filter_by(tenant_id=tenant.id, device_code=body.device_code)
        .first()
    )
    if exists:
        raise HTTPException(409, "device_code exists")
    d = Device(
        tenant_id=tenant.id,
        device_code=body.device_code,
        name=body.name,
        platform=body.platform,
        device_type=body.device_type,
        status="offline",
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"id": d.id, "device_code": d.device_code}


@app.post("/api/devices/heartbeat")
def heartbeat(body: HeartbeatIn, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter_by(code="default").first()
    d = (
        db.query(Device)
        .filter_by(tenant_id=tenant.id, device_code=body.device_code)
        .first()
    )
    if not d:
        d = Device(
            tenant_id=tenant.id,
            device_code=body.device_code,
            name=body.device_code,
            platform=body.platform,
            device_type="sim",
            status=body.status,
            last_seen_at=datetime.utcnow(),
        )
        db.add(d)
    else:
        d.status = body.status
        d.platform = body.platform
        d.last_seen_at = datetime.utcnow()
        d.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "device_code": body.device_code, "status": body.status}
