from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from app.api.deps import get_db, get_current_active_user
from app.api.v1.endpoints.roles import check_admin_permission  # 重用admin权限检查
from app.users.models import User as UserModel, Role as RoleModel, user_role
from app.services.menu import MenuService
from app.schemas.menu import (
    Menu, MenuCreate, MenuUpdate, MenuTree, 
    UserMenuResponse
)
from app.schemas.user import User

router = APIRouter()

# 本地admin权限检查函数
async def require_admin_role_for_menu(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """菜单管理专用的admin权限检查"""
    if not current_user.is_superuser:
        has_admin_role = await check_admin_permission(current_user.id, db)
        if not has_admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有admin角色可以执行此操作"
            )
    return current_user

# ==================== 管理员菜单管理 API ====================

@router.get("/admin/menus", response_model=List[Menu])
async def list_menus(
    skip: int = 0,
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role_for_menu)
):
    """获取所有菜单列表 - 仅admin"""
    menu_service = MenuService(db)
    menus = await menu_service.get_menus(skip=skip, limit=limit)
    # 转换为Pydantic模型，避免ORM关系问题
    result = []
    for menu in menus:
        # 解析meta
        meta = {}
        if menu.meta:
            try:
                meta = json.loads(menu.meta)
            except:
                meta = {}
        
        menu_dict = {
            "id": menu.id,
            "name": menu.name,
            "title": menu.title,
            "path": menu.path,
            "component": menu.component,
            "redirect": menu.redirect,
            "parent_id": menu.parent_id,
            "sort": menu.sort,
            "level": menu.level,
            "menu_type": menu.menu_type,
            "is_visible": menu.is_visible,
            "is_enabled": menu.is_enabled,
            "is_cache": menu.is_cache,
            "is_frame": menu.is_frame,
            "icon": menu.icon,
            "icon_type": menu.icon_type,
            "permission_code": menu.permission_code,
            "meta": meta,
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
            "children": []
        }
        result.append(Menu(**menu_dict))
    return result

@router.get("/admin/menus/tree", response_model=List[MenuTree])
async def get_menu_tree(
    include_disabled: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role_for_menu)
):
    """获取菜单树形结构 - 仅admin"""
    menu_service = MenuService(db)
    return await menu_service.get_menu_tree(include_disabled=include_disabled)

@router.post("/admin/menus", response_model=Menu)
async def create_menu(
    menu: MenuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role_for_menu)
):
    """创建菜单 - 仅admin"""
    menu_service = MenuService(db)
    
    # 检查菜单名是否已存在
    existing_menu = await menu_service.get_menu_by_name(menu.name)
    if existing_menu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="菜单名称已存在"
        )
    
    # 验证父菜单是否存在
    if menu.parent_id:
        parent_menu = await menu_service.get_menu(menu.parent_id)
        if not parent_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父菜单不存在"
            )
        
        # 检查层级限制
        if parent_menu.level >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="菜单层级不能超过5级"
            )
    
    return await menu_service.create_menu(menu)

@router.get("/admin/menus/{menu_id}", response_model=Menu)
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role_for_menu)
):
    """获取菜单详情 - 仅admin"""
    menu_service = MenuService(db)
    menu_obj = await menu_service.get_menu(menu_id)
    if not menu_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 转换为Pydantic模型
    meta = {}
    if menu_obj.meta:
        try:
            meta = json.loads(menu_obj.meta)
        except:
            meta = {}
    
    menu_dict = {
        "id": menu_obj.id,
        "name": menu_obj.name,
        "title": menu_obj.title,
        "path": menu_obj.path,
        "component": menu_obj.component,
        "redirect": menu_obj.redirect,
        "parent_id": menu_obj.parent_id,
        "sort": menu_obj.sort,
        "level": menu_obj.level,
        "menu_type": menu_obj.menu_type,
        "is_visible": menu_obj.is_visible,
        "is_enabled": menu_obj.is_enabled,
        "is_cache": menu_obj.is_cache,
        "is_frame": menu_obj.is_frame,
        "icon": menu_obj.icon,
        "icon_type": menu_obj.icon_type,
        "permission_code": menu_obj.permission_code,
        "meta": meta,
        "created_at": menu_obj.created_at,
        "updated_at": menu_obj.updated_at,
        "children": []
    }
    return Menu(**menu_dict)

@router.put("/admin/menus/{menu_id}", response_model=Menu)
async def update_menu(
    menu_id: int,
    menu_update: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role_for_menu)
):
    """更新菜单 - 仅admin"""
    menu_service = MenuService(db)
    
    # 检查菜单是否存在
    existing_menu = await menu_service.get_menu(menu_id)
    if not existing_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 检查名称冲突
    if menu_update.name:
        name_conflict = await menu_service.get_menu_by_name(menu_update.name)
        if name_conflict and name_conflict.id != menu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="菜单名称已存在"
            )
    
    # 验证父菜单
    if menu_update.parent_id is not None:
        if menu_update.parent_id == menu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将自己设为父菜单"
            )
        
        if menu_update.parent_id != 0:  # 0表示设为顶级菜单
            parent_menu = await menu_service.get_menu(menu_update.parent_id)
            if not parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父菜单不存在"
                )
            
            # 检查是否会形成循环引用
            if await _check_circular_reference(menu_service, menu_id, menu_update.parent_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能设置子菜单为父菜单，会形成循环引用"
                )
    
    updated_menu = await menu_service.update_menu(menu_id, menu_update)
    if not updated_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    return updated_menu

@router.delete("/admin/menus/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role_for_menu)
):
    """删除菜单 - 仅admin"""
    menu_service = MenuService(db)
    
    # 检查菜单是否存在
    existing_menu = await menu_service.get_menu(menu_id)
    if not existing_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    success = await menu_service.delete_menu(menu_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除菜单失败"
        )
    
    return {"message": "菜单删除成功"}

# ==================== 用户菜单 API ====================

@router.get("/menus/user", response_model=UserMenuResponse)
async def get_user_menus(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的菜单和路由"""
    menu_service = MenuService(db)
    return await menu_service.get_user_menus(current_user)

@router.get("/menus/tree", response_model=List[MenuTree])
async def get_user_menu_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的菜单树"""
    menu_service = MenuService(db)
    user_menus = await menu_service.get_user_menus(current_user)
    return user_menus.menus

# ==================== 辅助函数 ====================

async def _check_circular_reference(menu_service: MenuService, menu_id: int, parent_id: int) -> bool:
    """检查是否会形成循环引用"""
    current_id = parent_id
    max_depth = 10  # 防止无限循环
    depth = 0
    
    while current_id and depth < max_depth:
        if current_id == menu_id:
            return True  # 发现循环引用
        
        parent_menu = await menu_service.get_menu(current_id)
        if not parent_menu:
            break
        
        current_id = parent_menu.parent_id
        depth += 1
    
    return False 