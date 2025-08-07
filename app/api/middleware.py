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

# 添加日志
from app.core.logging import get_logger, log_auth, log_error

settings = get_settings()
logger = get_logger("auth")

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
            logger.debug(f"🔑 Found Bearer token: {token[:20]}...")
            
            user_info = await self._verify_jwt_token(token)
            if user_info:
                username = user_info["username"]
                log_auth(username, "Bearer token验证成功", True)
                return AuthCredentials(["authenticated"]), SimpleUser(username)
            else:
                logger.warning("🔑 Bearer token验证失败")
        
        # 2. 尝试从 Cookie 获取 token
        cookie_token = request.cookies.get("cmdb_auth")
        if cookie_token:
            logger.debug(f"🍪 Found cookie token: {cookie_token[:20]}...")
            
            user_info = await self._verify_jwt_token(cookie_token)
            if user_info:
                username = user_info["username"]
                log_auth(username, "Cookie token验证成功", True)
                return AuthCredentials(["authenticated"]), SimpleUser(username)
            else:
                logger.warning("🍪 Cookie token验证失败")
        
        # 3. 为匿名用户提供默认身份，让 Casbin 处理权限检查
        logger.debug("返回匿名用户身份")
        log_auth("anonymous", "使用匿名身份", True)
        return AuthCredentials(["anonymous"]), SimpleUser("anonymous")
    
    async def _verify_jwt_token(self, token: str) -> Optional[dict]:
        """验证 JWT token 并返回用户信息"""
        try:
            logger.debug("🔍 开始解码JWT token")
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"],
                options={"verify_aud": False}  # 跳过audience验证
            )
            user_id: int = payload.get("sub")
            if user_id is None:
                logger.warning("JWT payload中缺少用户ID")
                return None
            
            logger.debug(f"JWT解码成功，用户ID: {user_id}")
            
            # 从数据库获取用户信息
            async for db in get_db():
                stmt = select(User).filter(User.id == user_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user and user.is_active:
                    logger.info(f"👤 用户验证成功: {user.username} (ID: {user.id})")
                    return {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_superuser": user.is_superuser
                    }
                else:
                    if user:
                        logger.warning(f"用户未激活: {user.username}")
                    else:
                        logger.warning(f"用户不存在: ID {user_id}")
                break
            
            return None
            
        except JWTError as e:
            logger.warning(f"JWT验证失败: {type(e).__name__}: {str(e)}")
            log_error(e, "JWT验证")
            return None
        except Exception as e:
            logger.error(f"💥 用户验证过程中发生错误: {type(e).__name__}: {str(e)}")
            log_error(e, "用户验证")
            return None

class BasicAuthBackend(AuthenticationBackend):
    """
    基础认证后端（用于测试）
    支持 username:password 格式的 Basic Auth
    """
    
    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, SimpleUser]]:
        if "Authorization" not in request.headers:
            logger.debug("📭 没有Authorization header，返回匿名用户")
            return AuthCredentials(["anonymous"]), SimpleUser("anonymous")

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                logger.debug(f"非Basic认证方案: {scheme}")
                return AuthCredentials(["anonymous"]), SimpleUser("anonymous")
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as e:
            logger.error(f"Basic Auth凭据解码失败: {e}")
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        
        # 这里可以添加实际的用户验证逻辑
        # 为了演示，我们接受任何用户名和密码
        logger.info(f"🔐 Basic Auth: {username}")
        log_auth(username, "Basic Auth", True)
        return AuthCredentials(["authenticated"]), SimpleUser(username) 