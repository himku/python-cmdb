from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import verify_token
from app.database.session import SessionLocal
from app.users.models import User
from app.schemas.auth import TokenPayload

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
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

    # 兼容 sub 可能为用户id或用户名
    user = None
    if hasattr(token_data, "sub") and token_data.sub:
        # 优先按 id 查找
        user = db.query(User).filter(
            (User.id == token_data.sub) | (User.username == token_data.sub) | (User.email == token_data.sub)
        ).first()
    if not user:
        raise credentials_exception
    return user
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
