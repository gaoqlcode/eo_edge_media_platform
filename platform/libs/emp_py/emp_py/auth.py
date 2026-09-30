"""
文件：emp_py/auth.py
内容：企业级鉴权 — API Key 与 JWT 双模（任一通过即可）
Header:
  - X-API-Key: <key>           服务间 / 边端
  - Authorization: Bearer <jwt>  人工登录（BFF 签发）
"""
import os
from typing import Any, Dict, Optional

from fastapi import Header, HTTPException


def _api_key_ok(x_api_key: Optional[str]) -> bool:
    expected = os.getenv("EMP_API_KEY", "emp-dev-key")
    return bool(x_api_key) and x_api_key == expected


def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """仅 API Key（兼容旧代码）。"""
    if not _api_key_ok(x_api_key):
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")
    return x_api_key


def require_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    双模鉴权：API Key 或 Bearer JWT。
    返回身份字典：{"mode": "api_key"|"jwt", "sub": str, "role": str}
    """
    if _api_key_ok(x_api_key):
        return {"mode": "api_key", "sub": "service", "role": "service"}

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
        detail="need X-API-Key or Authorization: Bearer <jwt>",
    )
