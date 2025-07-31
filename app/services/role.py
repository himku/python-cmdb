from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.users.models import Role, Permission, User, user_role, role_permission
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取角色列表"""
        stmt = select(Role).options(selectinload(Role.permissions)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_role(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        stmt = select(Role).options(selectinload(Role.permissions), selectinload(Role.users)).filter(Role.id == role_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        stmt = select(Role).filter(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_role(self, role: RoleCreate) -> Role:
        """创建新角色"""
        db_role = Role(
            name=role.name,
            description=role.description
        )
        self.db.add(db_role)
        await self.db.commit()
        await self.db.refresh(db_role)
        return db_role
    
    async def update_role(self, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
        """更新角色信息"""
        db_role = await self.get_role(role_id)
        if not db_role:
            return None
        
        # 更新基本信息
        if role_update.name is not None:
            db_role.name = role_update.name
        if role_update.description is not None:
            db_role.description = role_update.description
        
        # 更新权限关联
        if role_update.permission_ids is not None:
            # 清除现有权限
            stmt = delete(role_permission).where(role_permission.c.role_id == role_id)
            await self.db.execute(stmt)
            
            # 添加新权限
            if role_update.permission_ids:
                for permission_id in role_update.permission_ids:
                    stmt = role_permission.insert().values(role_id=role_id, permission_id=permission_id)
                    await self.db.execute(stmt)
        
        await self.db.commit()
        await self.db.refresh(db_role)
        return db_role
    
    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        db_role = await self.get_role(role_id)
        if not db_role:
            return False
        
        # 先清除角色的所有关联
        # 清除用户-角色关联
        stmt = delete(user_role).where(user_role.c.role_id == role_id)
        await self.db.execute(stmt)
        
        # 清除角色-权限关联
        stmt = delete(role_permission).where(role_permission.c.role_id == role_id)
        await self.db.execute(stmt)
        
        # 删除角色
        await self.db.delete(db_role)
        await self.db.commit()
        return True
    
    async def assign_permission_to_role(self, role_id: int, permission_id: int) -> bool:
        """为角色分配权限"""
        # 检查角色和权限是否存在
        role = await self.get_role(role_id)
        if not role:
            return False
        
        stmt = select(Permission).filter(Permission.id == permission_id)
        result = await self.db.execute(stmt)
        permission = result.scalar_one_or_none()
        if not permission:
            return False
        
        # 检查是否已经存在关联
        stmt = select(role_permission).where(
            (role_permission.c.role_id == role_id) & 
            (role_permission.c.permission_id == permission_id)
        )
        result = await self.db.execute(stmt)
        if result.first():
            return True  # 已存在，返回成功
        
        # 创建关联
        stmt = role_permission.insert().values(role_id=role_id, permission_id=permission_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True
    
    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """从角色中移除权限"""
        stmt = delete(role_permission).where(
            (role_permission.c.role_id == role_id) & 
            (role_permission.c.permission_id == permission_id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def assign_role_to_user(self, user_id: int, role_id: int) -> bool:
        """为用户分配角色"""
        # 检查用户和角色是否存在
        stmt = select(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False
        
        role = await self.get_role(role_id)
        if not role:
            return False
        
        # 检查是否已经存在关联
        stmt = select(user_role).where(
            (user_role.c.user_id == user_id) & 
            (user_role.c.role_id == role_id)
        )
        result = await self.db.execute(stmt)
        if result.first():
            return True  # 已存在，返回成功
        
        # 创建关联
        stmt = user_role.insert().values(user_id=user_id, role_id=role_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True
    
    async def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """从用户中移除角色"""
        stmt = delete(user_role).where(
            (user_role.c.user_id == user_id) & 
            (user_role.c.role_id == role_id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_user_roles(self, user_id: int) -> List[Role]:
        """获取用户的所有角色"""
        stmt = select(Role).join(user_role).filter(user_role.c.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_role_permissions(self, role_id: int) -> List[Permission]:
        """获取角色的所有权限"""
        stmt = select(Permission).join(role_permission).filter(role_permission.c.role_id == role_id)
        result = await self.db.execute(stmt)
        return result.scalars().all() 