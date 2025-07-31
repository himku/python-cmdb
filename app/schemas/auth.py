from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None  # 改为整数类型，匹配新的用户ID
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