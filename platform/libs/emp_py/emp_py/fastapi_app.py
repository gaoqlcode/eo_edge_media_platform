"""
文件：emp_py/fastapi_app.py
内容：统一挂载健康检查、指标、请求日志与追踪中间件
"""
import time
import uuid

from fastapi import FastAPI, Request, Response

from emp_py.logging_setup import setup_logging
from emp_py.metrics import inc, render_prometheus
from emp_py.tracing import extract_or_create_trace_id, set_trace_id


def create_service_app(service_name: str, version: str = "0.1.0") -> FastAPI:
    app = FastAPI(title=f"EMP {service_name}", version=version)
    log = setup_logging(service_name)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        tid = extract_or_create_trace_id(
            request.headers.get("X-Trace-Id"),
            request.headers.get("traceparent"),
        )
        set_trace_id(tid)
        t0 = time.time()
        inc("emp_http_requests_total")
        try:
            response: Response = await call_next(request)
        except Exception:
            inc("emp_http_errors_total")
            log.error(f"unhandled path={request.url.path} trace={tid}")
            raise
        ms = int((time.time() - t0) * 1000)
        response.headers["X-Request-Id"] = rid
        response.headers["X-Trace-Id"] = tid
        response.headers["X-Response-Time-Ms"] = str(ms)
        log.info(
            f"method={request.method} path={request.url.path} "
            f"status={response.status_code} ms={ms} rid={rid} trace={tid}"
        )
        return response

    @app.get("/health")
    def health():
        return {"service": service_name, "status": "ok"}

    @app.get("/metrics")
    def metrics():
        return Response(content=render_prometheus(service_name), media_type="text/plain; version=0.0.4")

    return app
