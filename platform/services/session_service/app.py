"""
文件：session_service/app.py — 会话服务 + 统一健康/指标；写操作需 API Key
"""
import sys
from datetime import datetime
from pathlib import Path

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.audit import write_audit  # noqa: E402
from emp_py.auth import require_auth  # noqa: E402
from emp_py.db import get_db, init_db  # noqa: E402
from emp_py.fastapi_app import create_service_app  # noqa: E402
from emp_py.models import Device, RecordSession  # noqa: E402

app = create_service_app("session_service")


class SessionStart(BaseModel):
    device_code: str
    session_code: str
    storage_root: str = "data/sessions"


class SessionEnd(BaseModel):
    device_code: str
    session_code: str
    status: str = "closed"


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/sessions/start")
def start_session(
    body: SessionStart,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_auth),
):
    d = db.query(Device).filter_by(device_code=body.device_code).first()
    if not d:
        raise HTTPException(404, "device not found")
    exists = (
        db.query(RecordSession)
        .filter_by(device_id=d.id, session_code=body.session_code)
        .first()
    )
    if exists:
        raise HTTPException(409, "session exists")
    s = RecordSession(
        device_id=d.id,
        session_code=body.session_code,
        status="recording",
        started_at=datetime.utcnow(),
        storage_root=body.storage_root,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    out = {"id": s.id, "session_code": s.session_code, "status": s.status}
    write_audit(
        db,
        operator=str(auth.get("sub")),
        command="session.start",
        request=body.dict(),
        result=out,
        device_id=d.id,
    )
    return out


@app.post("/api/sessions/end")
def end_session(
    body: SessionEnd,
    db: Session = Depends(get_db),
    _auth: dict = Depends(require_auth),
):
    d = db.query(Device).filter_by(device_code=body.device_code).first()
    if not d:
        raise HTTPException(404, "device not found")
    s = (
        db.query(RecordSession)
        .filter_by(device_id=d.id, session_code=body.session_code)
        .first()
    )
    if not s:
        raise HTTPException(404, "session not found")
    s.status = body.status
    s.ended_at = datetime.utcnow()
    db.commit()
    return {"id": s.id, "status": s.status}


@app.get("/api/sessions")
def list_sessions(_auth: dict = Depends(require_auth), db: Session = Depends(get_db)):
    rows = db.query(RecordSession).order_by(RecordSession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "device_id": s.device_id,
            "session_code": s.session_code,
            "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "storage_root": s.storage_root,
        }
        for s in rows
    ]
