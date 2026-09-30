"""
文件：emp_py/idempotency.py
内容：基于 Redis（或内存）的事件幂等闸门 — SETNX
"""
import hashlib
from typing import Optional

from emp_py.redis_client import get_redis

_memory_seen = set()


def already_processed(event_id: Optional[str], body: str = "", ttl: int = 86400) -> bool:
    """
    若已处理过返回 True（调用方应跳过并 ack）。
    首次见到返回 False 并登记。
    """
    key = event_id or hashlib.sha256(body.encode("utf-8")).hexdigest()
    redis_key = f"emp:idem:{key}"
    r = get_redis()
    if r is not None:
        # SET NX EX：只有第一次成功
        ok = r.set(redis_key, "1", nx=True, ex=ttl)
        return ok is None or ok is False
    if key in _memory_seen:
        return True
    _memory_seen.add(key)
    return False
