from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.models import User
from app.users.manager import get_user_manager
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, CookieTransport, BearerTransport, AuthenticationBackend
from app.core.config import get_settings
from app.schemas.user import UserCreate, User, UserUpdate

settings = get_settings()

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

cookie_transport = CookieTransport(cookie_name="cmdb_auth", cookie_max_age=3600)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

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

fastapi_users = FastAPIUsers[User, str](
    get_user_manager,
    [auth_backend_cookie, auth_backend_bearer],
)

app = FastAPI()

# 注册 BearerTransport 路由，返回 200+JSON
app.include_router(
    fastapi_users.get_auth_router(auth_backend_bearer),
    prefix="/auth/jwt",
    tags=["auth"],
)
# 保留 CookieTransport 路由（如需前端 cookie 认证）
app.include_router(
    fastapi_users.get_auth_router(auth_backend_cookie),
    prefix="/auth/jwt-cookie",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserCreate, User),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(User, UserUpdate),
    prefix="/users",
    tags=["users"],
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "CMDB API is running smoothly."}
