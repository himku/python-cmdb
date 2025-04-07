from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[datetime] = None

class LoginData(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: Optional[list[str]] = None 