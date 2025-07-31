from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.deps import get_db, get_current_active_user
from app.services.role import RoleService
from app.services.permission import PermissionService
from app.schemas.role import Role, RoleCreate, RoleUpdate, Permission, PermissionCreate
from app.schemas.user import User
from app.users.models import User as UserModel, Role as RoleModel, user_role

router = APIRouter()

async def check_admin_permission(user_id: int, db: AsyncSession) -> bool:
    """检查用户是否有admin权限"""
    # 异步查询用户角色
    stmt = select(RoleModel.name).join(user_role).filter(user_role.c.user_id == user_id)
    result = await db.execute(stmt)
    user_roles = result.scalars().all()
    
    # 检查用户是否有admin角色
    return any(role.lower() == 'admin' for role in user_roles)

async def require_admin_role(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """确保当前用户具有admin角色"""
    if not current_user.is_superuser:
        has_admin_role = await check_admin_permission(current_user.id, db)
        if not has_admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有admin角色可以执行此操作"
            )
    return current_user

# ==================== 角色管理 API ====================

@router.get("/roles/", response_model=List[Role])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """获取所有角色列表 - 仅admin"""
    role_service = RoleService(db)
    return await role_service.get_roles(skip=skip, limit=limit)

@router.post("/roles/", response_model=Role)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """创建新角色 - 仅admin"""
    role_service = RoleService(db)
    
    # 检查角色名是否已存在
    existing_role = await role_service.get_role_by_name(role.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名已存在"
        )
    
    return await role_service.create_role(role)

@router.get("/roles/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """获取角色详情 - 仅admin"""
    role_service = RoleService(db)
    role = await role_service.get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role

@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """更新角色信息 - 仅admin"""
    role_service = RoleService(db)
    
    # 防止修改admin角色
    existing_role = await role_service.get_role(role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    if existing_role.name.lower() == 'admin' and role_update.name and role_update.name.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改admin角色的名称"
        )
    
    updated_role = await role_service.update_role(role_id, role_update)
    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return updated_role

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """删除角色 - 仅admin"""
    role_service = RoleService(db)
    
    # 防止删除admin角色
    existing_role = await role_service.get_role(role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    if existing_role.name.lower() == 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除admin角色"
        )
    
    success = await role_service.delete_role(role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return {"message": "角色删除成功"}

# ==================== 权限管理 API ====================

@router.get("/permissions/", response_model=List[Permission])
async def list_permissions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """获取所有权限列表 - 仅admin"""
    permission_service = PermissionService(db)
    return await permission_service.get_permissions(skip=skip, limit=limit)

@router.post("/permissions/", response_model=Permission)
async def create_permission(
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """创建新权限 - 仅admin"""
    permission_service = PermissionService(db)
    
    # 检查权限代码是否已存在
    existing_permission = await permission_service.get_permission_by_code(permission.code)
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限代码已存在"
        )
    
    return await permission_service.create_permission(permission)

@router.get("/permissions/{permission_id}", response_model=Permission)
async def get_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """获取权限详情 - 仅admin"""
    permission_service = PermissionService(db)
    permission = await permission_service.get_permission(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return permission

@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """删除权限 - 仅admin"""
    permission_service = PermissionService(db)
    success = await permission_service.delete_permission(permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return {"message": "权限删除成功"}

# ==================== 角色权限关联 API ====================

@router.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """为角色分配权限 - 仅admin"""
    role_service = RoleService(db)
    success = await role_service.assign_permission_to_role(role_id, permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配权限失败，请检查角色和权限是否存在"
        )
    return {"message": "权限分配成功"}

@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """从角色中移除权限 - 仅admin"""
    role_service = RoleService(db)
    success = await role_service.remove_permission_from_role(role_id, permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="移除权限失败"
        )
    return {"message": "权限移除成功"}

# ==================== 用户角色分配 API ====================

@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """为用户分配角色 - 仅admin"""
    role_service = RoleService(db)
    success = await role_service.assign_role_to_user(user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配角色失败，请检查用户和角色是否存在"
        )
    return {"message": "角色分配成功"}

@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """从用户中移除角色 - 仅admin"""
    role_service = RoleService(db)
    
    # 防止移除admin用户的admin角色
    if current_user.id == user_id:
        role = await role_service.get_role(role_id)
        if role and role.name.lower() == 'admin':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能移除自己的admin角色"
            )
    
    success = await role_service.remove_role_from_user(user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="移除角色失败"
        )
    return {"message": "角色移除成功"} 