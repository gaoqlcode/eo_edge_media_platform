"""
文件：emp_py/tracing.py
内容：轻量请求追踪（教学版 OpenTelemetry 前身）
- 接受/生成 X-Trace-Id（也认 traceparent 的 trace-id 段）
- 上下文变量供业务日志读取
生产可替换为 OTEL SDK，保持同样 Header 约定。
"""
import contextvars
import uuid
from typing import Optional

_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("emp_trace_id", default="")


def current_trace_id() -> str:
    return _trace_id.get() or ""


def set_trace_id(tid: str) -> None:
    _trace_id.set(tid)


def extract_or_create_trace_id(
    x_trace_id: Optional[str] = None,
    traceparent: Optional[str] = None,
) -> str:
    """优先 X-Trace-Id，其次 W3C traceparent，否则新建。"""
    if x_trace_id and x_trace_id.strip():
        return x_trace_id.strip()[:64]
    if traceparent:
        # version-traceid-spanid-flags
        parts = traceparent.split("-")
        if len(parts) >= 2 and len(parts[1]) >= 16:
            return parts[1][:32]
    return uuid.uuid4().hex
