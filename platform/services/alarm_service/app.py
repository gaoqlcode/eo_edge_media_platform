"""
文件：alarm_service/app.py
"""
import sys
from pathlib import Path

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.audit import write_audit  # noqa: E402
from emp_py.auth import require_roles  # noqa: E402
from emp_py.db import get_db, init_db  # noqa: E402
from emp_py.fastapi_app import create_service_app  # noqa: E402
from emp_py.models import AlarmEvent, Device  # noqa: E402

app = create_service_app("alarm_service")


class AlarmIn(BaseModel):
    device_code: str = None
    severity: str = "info"
    code: str
    message: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/alarms")
def create_alarm(
    body: AlarmIn,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_roles("admin", "service", "operator")),
):
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
    out = {"id": a.id, "code": a.code}
    write_audit(
        db,
        operator=str(auth.get("sub")),
        command="alarm.create",
        request=body.dict(),
        result=out,
        device_id=device_id,
    )
    return out


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
def ack_alarm(
    alarm_id: str,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_roles("admin", "service", "operator")),
):
    a = db.query(AlarmEvent).filter_by(id=alarm_id).first()
    if not a:
        raise HTTPException(404, "alarm not found")
    a.acked = True
    db.commit()
    out = {"id": a.id, "acked": True}
    write_audit(
        db,
        operator=str(auth.get("sub")),
        command="alarm.ack",
        request={"alarm_id": alarm_id},
        result=out,
        device_id=a.device_id,
    )
    return out
