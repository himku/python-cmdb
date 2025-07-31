from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# 密码上下文，支持多种哈希算法
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"], 
    deprecated="auto",
    argon2__default_rounds=3
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码，支持argon2和bcrypt"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 如果passlib失败，尝试原始bcrypt方法作为备选
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """生成密码哈希，默认使用argon2"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        # FastAPI-Users生成的token包含audience，需要验证
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            audience=["fastapi-users:auth"]  # 验证audience
        )
        return payload
    except JWTError as e:
        # 如果audience验证失败，尝试不验证audience
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM],
                options={"verify_aud": False}  # 跳过audience验证
            )
            return payload
        except JWTError:
            return None 