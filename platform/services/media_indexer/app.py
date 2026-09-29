"""
文件：media_indexer/app.py
内容：媒体资产索引服务 — 登记文件元数据
"""
import sys
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.db import get_db, init_db  # noqa: E402
from emp_py.models import MediaAsset, RecordSession  # noqa: E402

app = FastAPI(title="EMP media_indexer", version="0.1.0")


class AssetIn(BaseModel):
    session_code: str
    asset_type: str
    relative_path: str
    byte_size: int = 0


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"service": "media_indexer", "status": "ok"}


@app.post("/api/assets")
def add_asset(body: AssetIn, db: Session = Depends(get_db)):
    s = db.query(RecordSession).filter_by(session_code=body.session_code).first()
    if not s:
        raise HTTPException(404, "session not found")
    a = MediaAsset(
        session_id=s.id,
        asset_type=body.asset_type,
        relative_path=body.relative_path,
        byte_size=body.byte_size,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id, "relative_path": a.relative_path}


@app.get("/api/assets")
def list_assets(session_code: str = None, db: Session = Depends(get_db)):
    q = db.query(MediaAsset)
    if session_code:
        s = db.query(RecordSession).filter_by(session_code=session_code).first()
        if not s:
            return []
        q = q.filter_by(session_id=s.id)
    rows = q.all()
    return [
        {
            "id": a.id,
            "session_id": a.session_id,
            "asset_type": a.asset_type,
            "relative_path": a.relative_path,
            "byte_size": a.byte_size,
        }
        for a in rows
    ]
