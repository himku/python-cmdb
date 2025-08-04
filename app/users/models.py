import sqlalchemy as sa
from sqlalchemy import Integer, String, Boolean, Column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from app.database.session import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    
    # FastAPI-Users必需字段
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # 自定义字段
    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())

class CasbinRule(Base):
    """Casbin 策略规则表 - 统一管理所有角色和权限"""
    __tablename__ = "casbin_rule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ptype = Column(String(255), nullable=False, comment="策略类型")
    v0 = Column(String(255), nullable=True, comment="主体/角色")
    v1 = Column(String(255), nullable=True, comment="对象/资源")
    v2 = Column(String(255), nullable=True, comment="动作/操作") 
    v3 = Column(String(255), nullable=True, comment="扩展字段")
    v4 = Column(String(255), nullable=True, comment="扩展字段")
    v5 = Column(String(255), nullable=True, comment="扩展字段")
    created_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
