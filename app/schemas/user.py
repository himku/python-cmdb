from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.schemas.role import Role  # Add this import if Role is defined in app/schemas/role.py

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

    class Config:
        from_attributes = True
        
class UserWithRoles(User):
    roles: List[Role] = []
class UserWithRoles(User):
    roles: List["Role"] = []