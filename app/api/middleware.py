import base64
import binascii
from typing import Optional, Tuple
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser
from starlette.requests import Request
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.core.config import get_settings
from app.database.session import get_db
from app.users.models import User
from sqlalchemy import select

settings = get_settings()

class CasbinAuthBackend(AuthenticationBackend):
    """
    与 Casbin 集成的认证后端
    从 JWT token 中提取用户信息，为 Casbin 提供用户身份
    """
    
    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, SimpleUser]]:
        # 1. 尝试从 Authorization header 获取 Bearer token
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            user_info = await self._verify_jwt_token(token)
            if user_info:
                return AuthCredentials(["authenticated"]), SimpleUser(user_info["username"])
        
        # 2. 尝试从 Cookie 获取 token
        cookie_token = request.cookies.get("cmdb_auth")
        if cookie_token:
            user_info = await self._verify_jwt_token(cookie_token)
            if user_info:
                return AuthCredentials(["authenticated"]), SimpleUser(user_info["username"])
        
        # 3. 为匿名用户提供默认身份，让 Casbin 处理权限检查
        return AuthCredentials(["anonymous"]), SimpleUser("anonymous")
    
    async def _verify_jwt_token(self, token: str) -> Optional[dict]:
        """验证 JWT token 并返回用户信息"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"],
                options={"verify_aud": False}  # 跳过audience验证
            )
            user_id: int = payload.get("sub")
            if user_id is None:
                return None
            
            # 从数据库获取用户信息
            async for db in get_db():
                stmt = select(User).filter(User.id == user_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user and user.is_active:
                    return {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_superuser": user.is_superuser
                    }
                break
            
            return None
            
        except JWTError:
            return None

class BasicAuthBackend(AuthenticationBackend):
    """
    基础认证后端（用于测试）
    支持 username:password 格式的 Basic Auth
    """
    
    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, SimpleUser]]:
        if "Authorization" not in request.headers:
            return AuthCredentials(["anonymous"]), SimpleUser("anonymous")

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return AuthCredentials(["anonymous"]), SimpleUser("anonymous")
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        
        # 这里可以添加实际的用户验证逻辑
        # 为了演示，我们接受任何用户名和密码
        return AuthCredentials(["authenticated"]), SimpleUser(username) 