"""
文件：emp_py/redis_client.py
内容：Redis 封装；连不上时降级为内存字典（保证单机可测）
"""
from typing import Optional

from emp_py.config import settings

_memory = {}


def get_redis():
    """返回 redis.Redis 或 None（失败时用内存降级）。"""
    try:
        import redis

        r = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        return r
    except Exception:
        return None


def cache_set(key: str, value: str, ttl: int = 30) -> None:
    """写入缓存；Redis 不可用时写进程内字典。"""
    r = get_redis()
    if r is not None:
        r.setex(key, ttl, value)
    else:
        _memory[key] = value


def cache_get(key: str) -> Optional[str]:
    """读取缓存。"""
    r = get_redis()
    if r is not None:
        return r.get(key)
    return _memory.get(key)
