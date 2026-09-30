"""
文件：emp_py/auth.py
内容：企业级鉴权 — API Key / 设备 Token / JWT；可选 RBAC
Header:
  - X-API-Key: <key>              服务间
  - X-Device-Token: <token>       边端设备凭证（可与 EMP_API_KEY 相同作开发默认）
  - Authorization: Bearer <jwt>   人工登录
"""
import os
from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, Header, HTTPException


def _api_key_ok(x_api_key: Optional[str]) -> bool:
    expected = os.getenv("EMP_API_KEY", "emp-dev-key")
    return bool(x_api_key) and x_api_key == expected


def _device_token_ok(token: Optional[str]) -> bool:
    """边端凭证；未单独配置时回退到 EMP_API_KEY，便于开发。"""
    if not token:
        return False
    expected = os.getenv("EMP_DEVICE_TOKEN") or os.getenv("EMP_API_KEY", "emp-dev-key")
    return token == expected


def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    if not _api_key_ok(x_api_key):
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")
    return x_api_key


def require_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    三模鉴权：服务 Key / 设备 Token / Bearer JWT。
    返回：{"mode", "sub", "role"}
    role: service | device | admin | operator | ...
    """
    if _api_key_ok(x_api_key):
        return {"mode": "api_key", "sub": "service", "role": "service"}

    if _device_token_ok(x_device_token):
        return {"mode": "device_token", "sub": "device", "role": "device"}

    if authorization and authorization.lower().startswith("bearer "):
        from emp_py.jwt_auth import SECRET

        try:
            import jwt
        except ImportError as e:
            raise HTTPException(501, "PyJWT not installed") from e
        token = authorization.split(" ", 1)[1].strip()
        try:
            claims = jwt.decode(token, SECRET, algorithms=["HS256"])
            return {
                "mode": "jwt",
                "sub": claims.get("sub", "unknown"),
                "role": claims.get("role", "operator"),
            }
        except Exception as e:
            raise HTTPException(401, f"invalid token: {e}") from e

    raise HTTPException(
        status_code=401,
        detail="need X-API-Key, X-Device-Token, or Authorization: Bearer <jwt>",
    )


def require_roles(*allowed: str) -> Callable:
    """
    RBAC：在 require_auth 之上限制角色。
    用法：Depends(require_roles("admin", "service"))
    """

    def _dep(auth: Dict[str, Any] = Depends(require_auth)) -> Dict[str, Any]:
        role = auth.get("role") or ""
        if role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"role '{role}' not in {list(allowed)}",
            )
        return auth

    return _dep
