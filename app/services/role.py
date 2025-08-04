"""
角色服务 - 基于Casbin的角色管理
完全使用casbin_rule表管理角色和权限
"""

from typing import List, Dict, Any
from app.services.casbin_service import CasbinService
from app.schemas.role import CasbinRole, CasbinPolicy
from app.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class RoleService:
    """基于Casbin的角色管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_roles(self) -> List[CasbinRole]:
        """获取所有Casbin角色及其用户"""
        # 从Casbin获取所有角色
        casbin_roles = CasbinService.get_all_roles()
        
        roles = []
        for role_name in casbin_roles:
            # 获取拥有此角色的用户
            users = CasbinService.get_users_for_role(role_name)
            
            # 创建角色描述
            description = self._get_role_description(role_name)
            
            role = CasbinRole(
                name=role_name,
                description=description,
                users=users
            )
            roles.append(role)
        
        return roles
    
    async def get_role_by_name(self, role_name: str) -> CasbinRole:
        """根据名称获取角色"""
        users = CasbinService.get_users_for_role(role_name)
        description = self._get_role_description(role_name)
        
        return CasbinRole(
            name=role_name,
            description=description,
            users=users
        )
    
    async def create_role(self, role_name: str, description: str = None) -> CasbinRole:
        """创建新角色（通过添加策略）"""
        # 在Casbin中，角色通过策略定义，这里我们可以添加一个默认策略
        # 例如：给角色分配基本权限
        success = CasbinService.add_policy(role_name, "/basic", "GET")
        
        if success:
            return CasbinRole(
                name=role_name,
                description=description or f"角色: {role_name}",
                users=[]
            )
        else:
            raise ValueError(f"无法创建角色: {role_name}")
    
    async def assign_role_to_user(self, username: str, role_name: str) -> bool:
        """为用户分配角色"""
        success = CasbinService.add_role_for_user(username, role_name)
        
        # 如果是admin角色，同时更新数据库中的is_superuser字段
        if success and role_name == "admin":
            await self._sync_superuser_status(username, True)
        
        return success
    
    async def remove_role_from_user(self, username: str, role_name: str) -> bool:
        """从用户移除角色"""
        success = CasbinService.delete_role_for_user(username, role_name)
        
        # 如果移除admin角色，检查是否需要更新is_superuser
        if success and role_name == "admin":
            # 检查用户是否还有其他admin权限
            remaining_roles = CasbinService.get_roles_for_user(username)
            if "admin" not in remaining_roles:
                await self._sync_superuser_status(username, False)
        
        return success
    
    async def get_user_roles(self, username: str) -> List[str]:
        """获取用户的所有角色"""
        return CasbinService.get_roles_for_user(username)
    
    async def get_role_policies(self, role_name: str) -> List[CasbinPolicy]:
        """获取角色的所有策略"""
        all_policies = CasbinService.get_all_policies()
        role_policies = []
        
        for policy in all_policies:
            if len(policy) >= 3 and policy[0] == role_name:
                role_policies.append(CasbinPolicy(
                    role=policy[0],
                    resource=policy[1],
                    action=policy[2]
                ))
        
        return role_policies
    
    def _get_role_description(self, role_name: str) -> str:
        """获取角色描述"""
        descriptions = {
            "admin": "系统管理员，拥有所有权限",
            "user_manager": "用户管理员，可以管理用户",
            "viewer": "查看者，只能查看信息",
            "authenticated": "已认证用户，可访问基本功能"
        }
        return descriptions.get(role_name, f"角色: {role_name}")
    
    async def _sync_superuser_status(self, username: str, is_superuser: bool):
        """同步用户的超级用户状态到数据库"""
        try:
            stmt = select(User).filter(User.username == username)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.is_superuser = is_superuser
                await self.db.commit()
        except Exception as e:
            print(f"同步超级用户状态失败: {e}")
            await self.db.rollback()
    
    async def sync_superusers_to_casbin(self) -> int:
        """同步数据库中的超级用户到Casbin admin角色"""
        stmt = select(User).filter(User.is_superuser == True)
        result = await self.db.execute(stmt)
        superusers = result.scalars().all()
        
        count = 0
        for user in superusers:
            success = CasbinService.add_role_for_user(user.username, "admin")
            if success:
                count += 1
        
        return count 