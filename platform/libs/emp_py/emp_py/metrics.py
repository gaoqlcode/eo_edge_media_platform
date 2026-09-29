"""
文件：emp_py/metrics.py
内容：极简 Prometheus 文本指标（无第三方依赖）
"""
import time
from collections import defaultdict
from threading import Lock

_lock = Lock()
_counters = defaultdict(int)
_start = time.time()


def inc(name: str, value: int = 1) -> None:
    with _lock:
        _counters[name] += value


def render_prometheus(service: str) -> str:
    lines = [
        f"# HELP emp_up 1 if process up",
        f"# TYPE emp_up gauge",
        f'emp_up{{service="{service}"}} 1',
        f"# HELP emp_uptime_seconds process uptime",
        f"# TYPE emp_uptime_seconds gauge",
        f'emp_uptime_seconds{{service="{service}"}} {time.time() - _start:.0f}',
    ]
    with _lock:
        items = list(_counters.items())
    for k, v in items:
        lines.append(f"# TYPE {k} counter")
        lines.append(f'{k}{{service="{service}"}} {v}')
    return "\n".join(lines) + "\n"
