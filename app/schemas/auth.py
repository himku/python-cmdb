from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None  # 时间戳是整数
    aud: Optional[list[str]] = None  # FastAPI-Users可能包含audience字段
    
    class Config:
        extra = "allow"  # 允许额外字段

class LoginData(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: Optional[list[str]] = None 