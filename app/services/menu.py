from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import json

from app.users.models import Menu, User, Role, Permission, user_role, role_permission
from app.schemas.menu import MenuCreate, MenuUpdate, MenuTree, MenuRoute, UserMenuResponse

class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_menus(self, skip: int = 0, limit: int = 1000) -> List[Menu]:
        """获取所有菜单列表"""
        stmt = select(Menu).order_by(Menu.level, Menu.sort, Menu.id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_menu(self, menu_id: int) -> Optional[Menu]:
        """根据ID获取菜单"""
        stmt = select(Menu).filter(Menu.id == menu_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_menu_by_name(self, name: str) -> Optional[Menu]:
        """根据名称获取菜单"""
        stmt = select(Menu).filter(Menu.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_menu(self, menu: MenuCreate) -> Menu:
        """创建菜单"""
        # 处理元数据
        meta_json = json.dumps(menu.meta, ensure_ascii=False) if menu.meta else None
        
        # 自动计算层级
        level = 1
        if menu.parent_id:
            parent = await self.get_menu(menu.parent_id)
            if parent:
                level = parent.level + 1
        
        db_menu = Menu(
            name=menu.name,
            title=menu.title,
            path=menu.path,
            component=menu.component,
            redirect=menu.redirect,
            parent_id=menu.parent_id,
            sort=menu.sort,
            level=level,
            menu_type=menu.menu_type,
            is_visible=menu.is_visible,
            is_enabled=menu.is_enabled,
            is_cache=menu.is_cache,
            is_frame=menu.is_frame,
            icon=menu.icon,
            icon_type=menu.icon_type,
            permission_code=menu.permission_code,
            meta=meta_json
        )
        
        self.db.add(db_menu)
        await self.db.commit()
        await self.db.refresh(db_menu)
        return db_menu
    
    async def update_menu(self, menu_id: int, menu_update: MenuUpdate) -> Optional[Menu]:
        """更新菜单"""
        db_menu = await self.get_menu(menu_id)
        if not db_menu:
            return None
        
        # 更新字段
        for field, value in menu_update.model_dump(exclude_unset=True).items():
            if field == "meta" and value is not None:
                value = json.dumps(value, ensure_ascii=False)
            setattr(db_menu, field, value)
        
        # 如果父级发生变化，重新计算层级
        if menu_update.parent_id is not None:
            if menu_update.parent_id == 0:
                db_menu.parent_id = None
                db_menu.level = 1
            else:
                parent = await self.get_menu(menu_update.parent_id)
                if parent:
                    db_menu.level = parent.level + 1
        
        await self.db.commit()
        await self.db.refresh(db_menu)
        return db_menu
    
    async def delete_menu(self, menu_id: int) -> bool:
        """删除菜单（及其所有子菜单）"""
        db_menu = await self.get_menu(menu_id)
        if not db_menu:
            return False
        
        # 递归删除所有子菜单
        await self._delete_menu_recursive(menu_id)
        await self.db.commit()
        return True
    
    async def _delete_menu_recursive(self, menu_id: int):
        """递归删除菜单及其子菜单"""
        # 查找所有子菜单
        stmt = select(Menu).filter(Menu.parent_id == menu_id)
        result = await self.db.execute(stmt)
        children = result.scalars().all()
        
        # 递归删除子菜单
        for child in children:
            await self._delete_menu_recursive(child.id)
        
        # 删除当前菜单
        stmt = delete(Menu).where(Menu.id == menu_id)
        await self.db.execute(stmt)
    
    async def get_menu_tree(self, include_disabled: bool = False) -> List[MenuTree]:
        """获取菜单树形结构"""
        # 构建查询条件
        conditions = [Menu.level == 1]  # 只获取顶级菜单
        if not include_disabled:
            conditions.append(Menu.is_enabled == True)
        
        stmt = select(Menu).filter(and_(*conditions)).order_by(Menu.sort, Menu.id)
        result = await self.db.execute(stmt)
        top_menus = result.scalars().all()
        
        # 递归构建树形结构
        menu_trees = []
        for menu in top_menus:
            tree = await self._build_menu_tree(menu, include_disabled)
            menu_trees.append(tree)
        
        return menu_trees
    
    async def _build_menu_tree(self, menu: Menu, include_disabled: bool = False) -> MenuTree:
        """递归构建单个菜单的树形结构"""
        # 解析元数据
        meta = {}
        if menu.meta:
            try:
                meta = json.loads(menu.meta)
            except:
                meta = {}
        
        # 查找子菜单
        conditions = [Menu.parent_id == menu.id]
        if not include_disabled:
            conditions.append(Menu.is_enabled == True)
        
        stmt = select(Menu).filter(and_(*conditions)).order_by(Menu.sort, Menu.id)
        result = await self.db.execute(stmt)
        children = result.scalars().all()
        
        # 递归构建子菜单
        child_trees = []
        for child in children:
            child_tree = await self._build_menu_tree(child, include_disabled)
            child_trees.append(child_tree)
        
        return MenuTree(
            id=menu.id,
            name=menu.name,
            title=menu.title,
            path=menu.path,
            component=menu.component,
            redirect=menu.redirect,
            parent_id=menu.parent_id,
            sort=menu.sort,
            level=menu.level,
            menu_type=menu.menu_type,
            is_visible=menu.is_visible,
            is_enabled=menu.is_enabled,
            is_cache=menu.is_cache,
            is_frame=menu.is_frame,
            icon=menu.icon,
            icon_type=menu.icon_type,
            permission_code=menu.permission_code,
            meta=meta,
            children=child_trees
        )
    
    async def get_user_menus(self, user: User) -> UserMenuResponse:
        """获取用户有权限的菜单和路由"""
        # 获取用户权限
        user_permissions = await self._get_user_permissions(user)
        
        # 获取用户可访问的菜单
        accessible_menus = await self._get_accessible_menus(user, user_permissions)
        
        # 构建菜单树
        menu_tree = await self._build_accessible_menu_tree(accessible_menus)
        
        # 生成前端路由配置
        routes = self._build_routes_from_menus(menu_tree)
        
        return UserMenuResponse(
            menus=menu_tree,
            routes=routes,
            permissions=user_permissions
        )
    
    async def _get_user_permissions(self, user: User) -> List[str]:
        """获取用户的所有权限代码"""
        permissions = set()
        
        # 如果是超级用户，返回所有权限
        if user.is_superuser:
            stmt = select(Permission.code).filter(Permission.code.isnot(None))
            result = await self.db.execute(stmt)
            all_permissions = result.scalars().all()
            permissions.update(all_permissions)
            
            # 也包含所有菜单的权限代码
            stmt = select(Menu.permission_code).filter(Menu.permission_code.isnot(None))
            result = await self.db.execute(stmt)
            menu_permissions = result.scalars().all()
            permissions.update(menu_permissions)
        else:
            # 获取用户角色的权限
            stmt = select(Permission.code).join(role_permission).join(Role).join(user_role).filter(
                user_role.c.user_id == user.id
            )
            result = await self.db.execute(stmt)
            role_permissions = result.scalars().all()
            permissions.update(role_permissions)
        
        return list(permissions)
    
    async def _get_accessible_menus(self, user: User, user_permissions: List[str]) -> List[Menu]:
        """获取用户可访问的菜单"""
        if user.is_superuser:
            # 超级用户可以访问所有启用的菜单
            stmt = select(Menu).filter(Menu.is_enabled == True).order_by(Menu.level, Menu.sort, Menu.id)
        else:
            # 普通用户只能访问有权限的菜单
            stmt = select(Menu).filter(
                and_(
                    Menu.is_enabled == True,
                    or_(
                        Menu.permission_code.is_(None),  # 无权限要求的菜单
                        Menu.permission_code.in_(user_permissions)  # 有权限的菜单
                    )
                )
            ).order_by(Menu.level, Menu.sort, Menu.id)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _build_accessible_menu_tree(self, menus: List[Menu]) -> List[MenuTree]:
        """构建用户可访问的菜单树"""
        # 按层级组织菜单
        menu_dict = {menu.id: menu for menu in menus}
        top_menus = [menu for menu in menus if menu.parent_id is None]
        
        def build_tree(menu: Menu) -> MenuTree:
            # 解析元数据
            meta = {}
            if menu.meta:
                try:
                    meta = json.loads(menu.meta)
                except:
                    meta = {}
            
            # 查找子菜单
            children = [build_tree(child) for child in menus if child.parent_id == menu.id]
            
            return MenuTree(
                id=menu.id,
                name=menu.name,
                title=menu.title,
                path=menu.path,
                component=menu.component,
                redirect=menu.redirect,
                parent_id=menu.parent_id,
                sort=menu.sort,
                level=menu.level,
                menu_type=menu.menu_type,
                is_visible=menu.is_visible,
                is_enabled=menu.is_enabled,
                is_cache=menu.is_cache,
                is_frame=menu.is_frame,
                icon=menu.icon,
                icon_type=menu.icon_type,
                permission_code=menu.permission_code,
                meta=meta,
                children=children
            )
        
        return [build_tree(menu) for menu in top_menus]
    
    def _build_routes_from_menus(self, menus: List[MenuTree]) -> List[MenuRoute]:
        """将菜单树转换为前端路由配置"""
        routes = []
        
        for menu in menus:
            # 只处理显示的菜单和路由类型的菜单
            if not menu.is_visible or menu.menu_type == 3:  # 跳过按钮类型
                continue
            
            route = MenuRoute(
                name=menu.name,
                path=menu.path or '/',
                component=menu.component,
                redirect=menu.redirect,
                meta={
                    "title": menu.title,
                    "icon": menu.icon,
                    "isCache": menu.is_cache,
                    "isFrame": menu.is_frame,
                    "permission": menu.permission_code,
                    **menu.meta
                }
            )
            
            # 递归处理子菜单
            if menu.children:
                child_routes = self._build_routes_from_menus(menu.children)
                if child_routes:
                    route.children = child_routes
            
            routes.append(route)
        
        return routes 