"""
初始化菜单数据的脚本
参考fastapi-naive-admin项目的菜单架构
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.users.models import Menu
from app.services.menu import MenuService
from app.schemas.menu import MenuCreate
import json

# 预定义的菜单数据 - 参考fastapi-naive-admin架构
DEFAULT_MENUS = [
    {
        "name": "dashboard",
        "title": "工作台", 
        "path": "/dashboard",
        "component": "views/dashboard/index.vue",
        "parent_id": None,
        "sort": 1,
        "menu_type": 2,  # 菜单
        "icon": "mdi:monitor-dashboard",
        "permission_code": "dashboard:view",
        "meta": {
            "keepAlive": True,
            "order": 1
        }
    },
    {
        "name": "system",
        "title": "系统管理",
        "path": "/system", 
        "component": "layout",
        "parent_id": None,
        "sort": 2,
        "menu_type": 1,  # 目录
        "icon": "mdi:cog",
        "permission_code": "system:manage",
        "meta": {
            "order": 2
        }
    },
    {
        "name": "system-user",
        "title": "用户管理",
        "path": "/system/user",
        "component": "views/system/user/index.vue",
        "parent_name": "system",  # 临时字段，用于查找父级
        "sort": 1,
        "menu_type": 2,
        "icon": "mdi:account-multiple",
        "permission_code": "user:manage",
        "meta": {
            "keepAlive": True
        }
    },
    {
        "name": "system-role",
        "title": "角色管理", 
        "path": "/system/role",
        "component": "views/system/role/index.vue",
        "parent_name": "system",
        "sort": 2,
        "menu_type": 2,
        "icon": "mdi:account-key",
        "permission_code": "role:manage",
        "meta": {
            "keepAlive": True
        }
    },
    {
        "name": "system-permission",
        "title": "权限管理",
        "path": "/system/permission", 
        "component": "views/system/permission/index.vue",
        "parent_name": "system",
        "sort": 3,
        "menu_type": 2,
        "icon": "mdi:shield-key",
        "permission_code": "permission:manage",
        "meta": {
            "keepAlive": True
        }
    },
    {
        "name": "system-menu",
        "title": "菜单管理",
        "path": "/system/menu",
        "component": "views/system/menu/index.vue", 
        "parent_name": "system",
        "sort": 4,
        "menu_type": 2,
        "icon": "mdi:menu",
        "permission_code": "menu:manage",
        "meta": {
            "keepAlive": True
        }
    },
    # 用户管理按钮权限
    {
        "name": "user-add",
        "title": "新增用户",
        "path": "",
        "component": "",
        "parent_name": "system-user", 
        "sort": 1,
        "menu_type": 3,  # 按钮
        "icon": "",
        "permission_code": "user:add",
        "is_visible": False,
        "meta": {}
    },
    {
        "name": "user-edit", 
        "title": "编辑用户",
        "path": "",
        "component": "",
        "parent_name": "system-user",
        "sort": 2,
        "menu_type": 3,
        "icon": "",
        "permission_code": "user:edit",
        "is_visible": False,
        "meta": {}
    },
    {
        "name": "user-delete",
        "title": "删除用户",
        "path": "",
        "component": "",
        "parent_name": "system-user",
        "sort": 3,
        "menu_type": 3,
        "icon": "",
        "permission_code": "user:delete", 
        "is_visible": False,
        "meta": {}
    },
    # 角色管理按钮权限
    {
        "name": "role-add",
        "title": "新增角色",
        "path": "",
        "component": "",
        "parent_name": "system-role",
        "sort": 1,
        "menu_type": 3,
        "icon": "",
        "permission_code": "role:add",
        "is_visible": False,
        "meta": {}
    },
    {
        "name": "role-edit",
        "title": "编辑角色", 
        "path": "",
        "component": "",
        "parent_name": "system-role",
        "sort": 2,
        "menu_type": 3,
        "icon": "",
        "permission_code": "role:edit",
        "is_visible": False,
        "meta": {}
    },
    {
        "name": "role-delete",
        "title": "删除角色",
        "path": "",
        "component": "",
        "parent_name": "system-role",
        "sort": 3,
        "menu_type": 3,
        "icon": "",
        "permission_code": "role:delete",
        "is_visible": False,
        "meta": {}
    }
]

async def init_menus(db: AsyncSession) -> dict:
    """初始化菜单数据"""
    menu_service = MenuService(db)
    created_menus = {}
    
    print("正在初始化菜单...")
    
    # 第一轮：创建顶级菜单（parent_id为None的）
    for menu_data in DEFAULT_MENUS:
        if menu_data.get("parent_id") is None and "parent_name" not in menu_data:
            existing_menu = await menu_service.get_menu_by_name(menu_data["name"])
            if existing_menu:
                print(f"菜单 '{menu_data['title']}' 已存在，跳过创建")
                created_menus[menu_data["name"]] = existing_menu
                continue
            
            menu_create = MenuCreate(**{k: v for k, v in menu_data.items() if k != "parent_name"})
            
            try:
                new_menu = await menu_service.create_menu(menu_create)
                created_menus[menu_data["name"]] = new_menu
                print(f"✅ 创建顶级菜单: {menu_data['title']}")
            except Exception as e:
                print(f"❌ 创建菜单失败: {menu_data['title']} - {str(e)}")
    
    # 第二轮：创建子菜单
    for menu_data in DEFAULT_MENUS:
        if "parent_name" in menu_data:
            existing_menu = await menu_service.get_menu_by_name(menu_data["name"])
            if existing_menu:
                print(f"菜单 '{menu_data['title']}' 已存在，跳过创建")
                created_menus[menu_data["name"]] = existing_menu
                continue
            
            # 查找父菜单
            parent_name = menu_data.pop("parent_name")
            if parent_name in created_menus:
                menu_data["parent_id"] = created_menus[parent_name].id
                
                menu_create = MenuCreate(**menu_data)
                
                try:
                    new_menu = await menu_service.create_menu(menu_create)
                    created_menus[menu_data["name"]] = new_menu
                    print(f"✅ 创建子菜单: {menu_data['title']} (父级: {parent_name})")
                except Exception as e:
                    print(f"❌ 创建菜单失败: {menu_data['title']} - {str(e)}")
            else:
                print(f"⚠️  父菜单不存在: {parent_name}，跳过 {menu_data['title']}")
    
    return created_menus

async def init_menu_system():
    """初始化菜单系统的主函数"""
    print("🚀 开始初始化菜单系统...")
    
    async for db in get_db():
        try:
            # 初始化菜单
            menus = await init_menus(db)
            
            print("\n🎉 菜单系统初始化完成！")
            print(f"   - 创建/检查了 {len(DEFAULT_MENUS)} 个菜单项")
            print("   - 包含工作台、系统管理等核心菜单")
            print("   - 支持按钮级权限控制")
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            raise
        finally:
            break

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_menu_system()) 