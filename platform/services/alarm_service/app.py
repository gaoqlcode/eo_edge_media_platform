"""
文件：alarm_service/app.py
内容：告警微服务 — 创建/列表/确认
"""
import sys
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.db import get_db, init_db  # noqa: E402
from emp_py.models import AlarmEvent, Device  # noqa: E402

app = FastAPI(title="EMP alarm_service", version="0.1.0")


class AlarmIn(BaseModel):
    device_code: str = None
    severity: str = "info"
    code: str
    message: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"service": "alarm_service", "status": "ok"}


@app.post("/api/alarms")
def create_alarm(body: AlarmIn, db: Session = Depends(get_db)):
    device_id = None
    if body.device_code:
        d = db.query(Device).filter_by(device_code=body.device_code).first()
        device_id = d.id if d else None
    a = AlarmEvent(
        device_id=device_id,
        severity=body.severity,
        code=body.code,
        message=body.message,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id, "code": a.code}


@app.get("/api/alarms")
def list_alarms(db: Session = Depends(get_db)):
    rows = db.query(AlarmEvent).order_by(AlarmEvent.occurred_at.desc()).limit(100).all()
    return [
        {
            "id": a.id,
            "severity": a.severity,
            "code": a.code,
            "message": a.message,
            "acked": a.acked,
            "occurred_at": a.occurred_at.isoformat() if a.occurred_at else None,
        }
        for a in rows
    ]


@app.post("/api/alarms/{alarm_id}/ack")
def ack_alarm(alarm_id: str, db: Session = Depends(get_db)):
    a = db.query(AlarmEvent).filter_by(id=alarm_id).first()
    if not a:
        raise HTTPException(404, "alarm not found")
    a.acked = True
    db.commit()
    return {"id": a.id, "acked": True}
