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

class Menu(Base):
    """菜单模型 - 参考fastapi-naive-admin架构"""
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基础信息
    name = Column(String(100), nullable=False, comment="菜单名称")
    title = Column(String(100), nullable=False, comment="菜单标题(显示名称)")
    path = Column(String(255), nullable=True, comment="路由路径")
    component = Column(String(255), nullable=True, comment="组件路径")
    redirect = Column(String(255), nullable=True, comment="重定向地址")
    
    # 层级结构
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True, comment="父菜单ID")
    sort = Column(Integer, default=0, comment="排序序号")
    level = Column(Integer, default=1, comment="菜单层级")
    
    # 菜单类型和状态
    menu_type = Column(Integer, default=1, comment="菜单类型: 1-目录 2-菜单 3-按钮")
    is_visible = Column(Boolean, default=True, comment="是否显示")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    is_cache = Column(Boolean, default=False, comment="是否缓存")
    is_frame = Column(Boolean, default=False, comment="是否为外链")
    
    # 图标和样式
    icon = Column(String(100), nullable=True, comment="菜单图标")
    icon_type = Column(Integer, default=1, comment="图标类型: 1-iconify 2-本地")
    
    # 权限控制
    permission_code = Column(String(100), nullable=True, comment="权限标识码")
    
    # 元信息(JSON格式存储额外配置)
    meta = Column(sa.Text, nullable=True, comment="元数据配置")
    
    # 时间戳
    created_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    updated_at = Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    
    # 关系
    children = relationship("Menu", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("Menu", back_populates="children", remote_side=[id])
    
    def __repr__(self):
        return f"<Menu(id={self.id}, name='{self.name}', title='{self.title}')>"
