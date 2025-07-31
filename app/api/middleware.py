from typing import List
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import get_settings
from app.core.security import verify_token

settings = get_settings()
security = HTTPBearer()

# 不需要token认证的公开接口
PUBLIC_PATHS: List[str] = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/auth/logout", 
    "/auth/register",
    "/auth/jwt-cookie/login",
    "/auth/jwt-cookie/logout",
]

def is_public_path(path: str) -> bool:
    """检查路径是否为公开接口"""
    for public_path in PUBLIC_PATHS:
        if path.startswith(public_path):
            return True
    return False

async def verify_token_middleware(request: Request, call_next):
    """Token验证中间件"""
    
    # 检查是否为公开接口
    if is_public_path(request.url.path):
        response = await call_next(request)
        return response
    
    # 获取Authorization头
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 提取token
    token = authorization.split(" ")[1]
    
    try:
        # 验证token
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 继续处理请求
    response = await call_next(request)
    return response 