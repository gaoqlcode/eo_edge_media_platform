"""
文件：emp_py/audit.py
内容：写操作审计落库 command_audits（企业追责）
"""
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from emp_py.models import CommandAudit

log = logging.getLogger("emp.audit")


def _jsonable(obj: Any) -> Any:
    """把 UUID 等转为 JSON 可序列化结构。"""
    if obj is None:
        return None
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    return obj


def write_audit(
    db: Session,
    *,
    operator: str,
    command: str,
    request: Optional[Dict[str, Any]] = None,
    result: Optional[Dict[str, Any]] = None,
    device_id: Optional[str] = None,
) -> None:
    """写入一条审计；失败记录日志但不阻断主业务响应。"""
    try:
        did = str(device_id) if device_id is not None else None
        row = CommandAudit(
            device_id=did,
            operator=(operator or "unknown")[:64],
            command=command[:64],
            request_json=_jsonable(request) or {},
            result_json=_jsonable(result) or {},
        )
        db.add(row)
        db.commit()
    except Exception as e:
        log.exception("write_audit failed command=%s err=%s", command, e)
        try:
            db.rollback()
        except Exception:
            pass
