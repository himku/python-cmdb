"""
初始化角色和权限数据的脚本
创建admin角色和基础权限系统
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.users.models import Role, Permission, User, user_role, role_permission
from app.services.role import RoleService
from app.services.permission import PermissionService
from app.schemas.role import RoleCreate, PermissionCreate

# 预定义的权限列表
DEFAULT_PERMISSIONS = [
    {
        "name": "用户管理",
        "code": "user:manage",
        "description": "创建、编辑、删除用户"
    },
    {
        "name": "用户查看",
        "code": "user:read",
        "description": "查看用户信息"
    },
    {
        "name": "角色管理",
        "code": "role:manage", 
        "description": "创建、编辑、删除角色"
    },
    {
        "name": "权限管理",
        "code": "permission:manage",
        "description": "创建、编辑、删除权限"
    },
    {
        "name": "系统设置",
        "code": "system:config",
        "description": "修改系统配置"
    },
    {
        "name": "数据导出",
        "code": "data:export",
        "description": "导出系统数据"
    },
    {
        "name": "日志查看",
        "code": "log:read",
        "description": "查看系统日志"
    }
]

# 预定义的角色列表
DEFAULT_ROLES = [
    {
        "name": "admin",
        "description": "系统管理员，拥有所有权限",
        "permissions": ["user:manage", "user:read", "role:manage", "permission:manage", "system:config", "data:export", "log:read"]
    },
    {
        "name": "user_manager",
        "description": "用户管理员，可以管理用户",
        "permissions": ["user:manage", "user:read"]
    },
    {
        "name": "viewer",
        "description": "查看者，只能查看信息",
        "permissions": ["user:read", "log:read"]
    }
]

async def init_permissions(db: AsyncSession) -> dict:
    """初始化权限数据"""
    permission_service = PermissionService(db)
    created_permissions = {}
    
    print("正在初始化权限...")
    
    for perm_data in DEFAULT_PERMISSIONS:
        # 检查权限是否已存在
        existing_permission = await permission_service.get_permission_by_code(perm_data["code"])
        if existing_permission:
            print(f"权限 '{perm_data['name']}' 已存在，跳过创建")
            created_permissions[perm_data["code"]] = existing_permission
            continue
        
        # 创建新权限
        permission_create = PermissionCreate(
            name=perm_data["name"],
            code=perm_data["code"],
            description=perm_data["description"]
        )
        
        try:
            new_permission = await permission_service.create_permission(permission_create)
            created_permissions[perm_data["code"]] = new_permission
            print(f"✅ 创建权限: {perm_data['name']} ({perm_data['code']})")
        except Exception as e:
            print(f"❌ 创建权限失败: {perm_data['name']} - {str(e)}")
    
    return created_permissions

async def init_roles(db: AsyncSession, permissions: dict) -> dict:
    """初始化角色数据"""
    role_service = RoleService(db)
    created_roles = {}
    
    print("\n正在初始化角色...")
    
    for role_data in DEFAULT_ROLES:
        # 检查角色是否已存在
        existing_role = await role_service.get_role_by_name(role_data["name"])
        if existing_role:
            print(f"角色 '{role_data['name']}' 已存在，跳过创建")
            created_roles[role_data["name"]] = existing_role
            continue
        
        # 创建新角色
        role_create = RoleCreate(
            name=role_data["name"],
            description=role_data["description"]
        )
        
        try:
            new_role = await role_service.create_role(role_create)
            created_roles[role_data["name"]] = new_role
            print(f"✅ 创建角色: {role_data['name']}")
            
            # 为角色分配权限
            for perm_code in role_data["permissions"]:
                if perm_code in permissions:
                    permission = permissions[perm_code]
                    success = await role_service.assign_permission_to_role(new_role.id, permission.id)
                    if success:
                        print(f"   ✅ 为角色 '{role_data['name']}' 分配权限: {perm_code}")
                    else:
                        print(f"   ❌ 为角色 '{role_data['name']}' 分配权限失败: {perm_code}")
                else:
                    print(f"   ⚠️  权限不存在: {perm_code}")
            
        except Exception as e:
            print(f"❌ 创建角色失败: {role_data['name']} - {str(e)}")
    
    return created_roles

async def assign_admin_role_to_superusers(db: AsyncSession, roles: dict):
    """为所有超级用户分配admin角色"""
    if "admin" not in roles:
        print("❌ admin角色不存在，无法分配给超级用户")
        return
    
    admin_role = roles["admin"]
    role_service = RoleService(db)
    
    print("\n正在为超级用户分配admin角色...")
    
    # 查找所有超级用户
    stmt = select(User).filter(User.is_superuser == True)
    result = await db.execute(stmt)
    superusers = result.scalars().all()
    
    for user in superusers:
        try:
            success = await role_service.assign_role_to_user(user.id, admin_role.id)
            if success:
                print(f"✅ 为超级用户 '{user.username}' 分配admin角色")
            else:
                print(f"❌ 为超级用户 '{user.username}' 分配admin角色失败")
        except Exception as e:
            print(f"❌ 为超级用户 '{user.username}' 分配admin角色失败: {str(e)}")

async def init_roles_and_permissions():
    """初始化角色和权限系统的主函数"""
    print("🚀 开始初始化角色和权限系统...")
    
    async for db in get_db():
        try:
            # 1. 初始化权限
            permissions = await init_permissions(db)
            
            # 2. 初始化角色并分配权限
            roles = await init_roles(db, permissions)
            
            # 3. 为超级用户分配admin角色
            await assign_admin_role_to_superusers(db, roles)
            
            print("\n🎉 角色和权限系统初始化完成！")
            print(f"   - 创建/检查了 {len(DEFAULT_PERMISSIONS)} 个权限")
            print(f"   - 创建/检查了 {len(DEFAULT_ROLES)} 个角色")
            print("   - admin角色已分配给所有超级用户")
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            raise
        finally:
            break

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_roles_and_permissions()) 