"""
文件：emp_py/auth.py
内容：企业级最小鉴权 — API Key（Header: X-API-Key）
说明：生产可演进为 JWT；学习阶段先把「未授权拒绝」做实
"""
import os
from fastapi import Header, HTTPException


def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """校验网关/客户端传入的 API Key；失败抛 401。"""
    expected = os.getenv("EMP_API_KEY", "emp-dev-key")
    # 允许本地健康检查不带 key：由各路由决定是否依赖本函数
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")
    return x_api_key
