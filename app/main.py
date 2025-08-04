from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from app.users.models import User
from app.users.manager import get_user_manager
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, CookieTransport, BearerTransport, AuthenticationBackend
from app.core.config import get_settings
from app.schemas.user import User as UserRead, UserCreate
from app.schemas.auth import UserLogin
from app.services.casbin_service import CasbinService
from fastapi_authz import CasbinMiddleware
from app.api.middleware import CasbinAuthBackend

settings = get_settings()

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

cookie_transport = CookieTransport(cookie_name="cmdb_auth", cookie_max_age=3600)
bearer_transport = BearerTransport(tokenUrl="auth/login")

auth_backend_cookie = AuthenticationBackend(
    name="jwt_cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
auth_backend_bearer = AuthenticationBackend(
    name="jwt_bearer",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend_cookie, auth_backend_bearer],
)

from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="现代化的配置管理数据库(CMDB)系统，提供完整的资产管理、用户认证和企业级权限控制功能。",
)

# 中间件添加顺序很重要：后添加的先执行
# 1. 最先添加 CORS（最后执行）
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=settings.CORS_EXPOSE_HEADERS,
        max_age=settings.CORS_MAX_AGE,
    )

# 2. 添加 Casbin 权限控制中间件（倒数第二执行）
enforcer = CasbinService.get_enforcer()
app.add_middleware(CasbinMiddleware, enforcer=enforcer)

# 3. 最后添加认证中间件（最先执行）
app.add_middleware(AuthenticationMiddleware, backend=CasbinAuthBackend())

# 注册认证路由 - 使用自定义认证模型
app.include_router(
    fastapi_users.get_auth_router(auth_backend_bearer, requires_verification=False),
    prefix="/auth",
    tags=["auth"],
)
# 注册用户注册路由
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# 注册用户管理路由（包括 /users/me）
app.include_router(
    fastapi_users.get_users_router(UserRead, UserCreate),
    prefix="/users",
    tags=["users"],
)

# 保留 CookieTransport 路由（如需前端 cookie 认证）
app.include_router(
    fastapi_users.get_auth_router(auth_backend_cookie),
    prefix="/auth/jwt-cookie",
    tags=["auth"],
)

# 注册自定义 /users 路由（带权限控制）
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "message": "CMDB API is running smoothly.",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


