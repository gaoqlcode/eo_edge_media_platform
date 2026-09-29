"""
文件：emp_py/fastapi_app.py
内容：统一挂载健康检查、指标、请求日志中间件，供各微服务复用
"""
import time
import uuid

from fastapi import FastAPI, Request, Response

from emp_py.logging_setup import setup_logging
from emp_py.metrics import inc, render_prometheus


def create_service_app(service_name: str, version: str = "0.1.0") -> FastAPI:
    app = FastAPI(title=f"EMP {service_name}", version=version)
    log = setup_logging(service_name)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        t0 = time.time()
        inc("emp_http_requests_total")
        try:
            response: Response = await call_next(request)
        except Exception:
            inc("emp_http_errors_total")
            log.error(f"unhandled path={request.url.path}")
            raise
        ms = int((time.time() - t0) * 1000)
        response.headers["X-Request-Id"] = rid
        response.headers["X-Response-Time-Ms"] = str(ms)
        log.info(f"method={request.method} path={request.url.path} status={response.status_code} ms={ms} rid={rid}")
        return response

    @app.get("/health")
    def health():
        return {"service": service_name, "status": "ok"}

    @app.get("/metrics")
    def metrics():
        return Response(content=render_prometheus(service_name), media_type="text/plain; version=0.0.4")

    return app
