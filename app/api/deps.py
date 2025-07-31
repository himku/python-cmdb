from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import verify_token
from app.database.session import SessionLocal
from app.users.models import User
from app.schemas.auth import TokenPayload

settings = get_settings()
# 修正tokenUrl为正确的登录端点
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise credentials_exception

    # 根据sub字段查找用户
    user = None
    if hasattr(token_data, "sub") and token_data.sub:
        from sqlalchemy import select
        # 按用户ID查找
        stmt = select(User).filter(User.id == token_data.sub)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        # 如果按ID没找到，尝试按用户名或邮箱查找
        if not user:
            stmt = select(User).filter(
                (User.username == token_data.sub) | (User.email == token_data.sub)
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
    
    if not user:
        raise credentials_exception
    return user
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
