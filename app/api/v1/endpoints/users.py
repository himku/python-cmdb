from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# 正确的导入
from app.api.deps import get_db, get_current_active_user
from app.users.models import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, UserWithRoles
from app.services.user import UserService
from app.core.logging import get_logger, log_api_call, log_auth, log_error
from app.core.config import get_settings

logger = get_logger("users_api")
security = HTTPBearer()
router = APIRouter()
settings = get_settings()

@router.get("/cors-debug", summary="CORS调试信息")
async def cors_debug(request: Request):
    """获取CORS配置和请求信息，用于调试跨域问题"""
    logger.info("📡 CORS调试请求")
    
    headers = dict(request.headers)
    
    return {
        "cors_config": {
            "allowed_origins": settings.BACKEND_CORS_ORIGINS,
            "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
            "allow_methods": settings.CORS_ALLOW_METHODS,
            "allow_headers": settings.CORS_ALLOW_HEADERS,
            "expose_headers": settings.CORS_EXPOSE_HEADERS,
            "max_age": settings.CORS_MAX_AGE,
        },
        "request_info": {
            "method": request.method,
            "url": str(request.url),
            "origin": headers.get("origin"),
            "user_agent": headers.get("user-agent"),
            "referer": headers.get("referer"),
            "all_headers": headers
        },
        "environment": settings.ENVIRONMENT
    }

@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户列表"""
    log_api_call("/api/v1/users/", "GET", current_user.username)
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新用户"""
    log_api_call("/api/v1/users/", "POST", current_user.username)
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    db_user = await user_service.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await user_service.create_user(user=user)

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定用户信息"""
    log_api_call(f"/api/v1/users/{user_id}", "GET", current_user.username)
    
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    db_user = await user_service.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户信息"""
    log_api_call(f"/api/v1/users/{user_id}", "PUT", current_user.username)
    
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    db_user = await user_service.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await user_service.update_user(user_id=user_id, user=user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除用户"""
    log_api_call(f"/api/v1/users/{user_id}", "DELETE", current_user.username)
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users cannot delete themselves"
        )
    
    user_service = UserService(db)
    db_user = await user_service.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_service.delete_user(user_id=user_id)
    return {"message": "User deleted successfully"}
