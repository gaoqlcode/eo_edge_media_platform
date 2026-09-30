"""
文件：emp_py/jwt_auth.py
内容：JWT 签发/校验（HS256）；与 API Key 并存，BFF 登录后发 token
依赖：PyJWT（可选，缺失时接口返回 501）
"""
import os
import time
from typing import Optional

from fastapi import Header, HTTPException

SECRET = os.getenv("EMP_JWT_SECRET", "emp-jwt-dev-secret-change-me")
TTL_SEC = int(os.getenv("EMP_JWT_TTL", "3600"))


def issue_token(username: str, role: str = "operator") -> dict:
    try:
        import jwt
    except ImportError as e:
        raise HTTPException(501, "PyJWT not installed") from e
    now = int(time.time())
    payload = {"sub": username, "role": role, "iat": now, "exp": now + TTL_SEC}
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return {"access_token": token, "token_type": "bearer", "expires_in": TTL_SEC}


def require_jwt(authorization: Optional[str] = Header(None)) -> dict:
    """Authorization: Bearer <token>"""
    try:
        import jwt
    except ImportError as e:
        raise HTTPException(501, "PyJWT not installed") from e
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(401, f"invalid token: {e}") from e
