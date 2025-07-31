from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.users.models import Permission
from app.schemas.role import PermissionCreate

class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_permissions(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """获取权限列表"""
        stmt = select(Permission).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_permission(self, permission_id: int) -> Optional[Permission]:
        """根据ID获取权限"""
        stmt = select(Permission).filter(Permission.id == permission_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """根据代码获取权限"""
        stmt = select(Permission).filter(Permission.code == code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """根据名称获取权限"""
        stmt = select(Permission).filter(Permission.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_permission(self, permission: PermissionCreate) -> Permission:
        """创建新权限"""
        db_permission = Permission(
            name=permission.name,
            code=permission.code,
            description=permission.description
        )
        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)
        return db_permission
    
    async def delete_permission(self, permission_id: int) -> bool:
        """删除权限"""
        db_permission = await self.get_permission(permission_id)
        if not db_permission:
            return False
        
        await self.db.delete(db_permission)
        await self.db.commit()
        return True 