"""
文件：emp_py/tracing.py
内容：轻量追踪（OTEL 教学前身）
- X-Trace-Id / W3C traceparent
- span_id 上下文
- 日志用 span() 上下文管理器
生产可替换为 OpenTelemetry SDK，Header 约定保持兼容。
"""
import contextvars
import time
import uuid
from contextlib import contextmanager
from typing import Iterator, Optional

_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("emp_trace_id", default="")
_span_id: contextvars.ContextVar[str] = contextvars.ContextVar("emp_span_id", default="")


def current_trace_id() -> str:
    return _trace_id.get() or ""


def current_span_id() -> str:
    return _span_id.get() or ""


def set_trace_id(tid: str) -> None:
    _trace_id.set(tid)


def set_span_id(sid: str) -> None:
    _span_id.set(sid)


def new_span_id() -> str:
    return uuid.uuid4().hex[:16]


def extract_or_create_trace_id(
    x_trace_id: Optional[str] = None,
    traceparent: Optional[str] = None,
) -> str:
    if x_trace_id and x_trace_id.strip():
        return x_trace_id.strip()[:64]
    if traceparent:
        parts = traceparent.split("-")
        if len(parts) >= 2 and len(parts[1]) >= 16:
            return parts[1][:32]
    return uuid.uuid4().hex


def format_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """W3C traceparent: 00-<trace>-<span>-<flags>"""
    tid = (trace_id + "0" * 32)[:32]
    sid = (span_id + "0" * 16)[:16]
    flags = "01" if sampled else "00"
    return f"00-{tid}-{sid}-{flags}"


@contextmanager
def span(name: str, logger=None) -> Iterator[str]:
    """业务内嵌 span：记录起止，返回 span_id。"""
    parent = current_span_id()
    sid = new_span_id()
    token = _span_id.set(sid)
    t0 = time.time()
    if logger:
        logger.info(f"span_start name={name} span={sid} parent={parent} trace={current_trace_id()}")
    try:
        yield sid
    finally:
        ms = int((time.time() - t0) * 1000)
        if logger:
            logger.info(f"span_end name={name} span={sid} ms={ms} trace={current_trace_id()}")
        _span_id.reset(token)
