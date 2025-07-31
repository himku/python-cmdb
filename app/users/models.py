import sqlalchemy as sa
from sqlalchemy import Integer, String, Boolean, Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

# 用户-角色多对多关联表
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id"))
)

# 角色-权限多对多关联表
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id"))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    # 用户与角色多对多
    roles = relationship("Role", secondary=user_role, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    # 角色与用户多对多
    users = relationship("User", secondary=user_role, back_populates="roles")
    # 角色与权限多对多
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    # 权限与角色多对多
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")
