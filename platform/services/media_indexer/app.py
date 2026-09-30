"""
文件：media_indexer/app.py
"""
import sys
from pathlib import Path

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.auth import require_auth  # noqa: E402
from emp_py.db import get_db, init_db  # noqa: E402
from emp_py.fastapi_app import create_service_app  # noqa: E402
from emp_py.models import MediaAsset, RecordSession  # noqa: E402

app = create_service_app("media_indexer")


class AssetIn(BaseModel):
    session_code: str
    asset_type: str
    relative_path: str
    byte_size: int = 0


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/assets")
def add_asset(
    body: AssetIn,
    db: Session = Depends(get_db),
    _auth: dict = Depends(require_auth),
):
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


@app.get("/api/playback/{session_code}")
def playback_index(session_code: str, db: Session = Depends(get_db)):
    """回放索引：列出会话资产，供客户端按相对路径拉帧/成片。"""
    s = db.query(RecordSession).filter_by(session_code=session_code).first()
    if not s:
        raise HTTPException(404, "session not found")
    assets = db.query(MediaAsset).filter_by(session_id=s.id).all()
    return {
        "session_code": session_code,
        "status": s.status,
        "storage_root": s.storage_root,
        "assets": [
            {
                "asset_type": a.asset_type,
                "relative_path": a.relative_path,
                "byte_size": a.byte_size,
            }
            for a in assets
        ],
    }
