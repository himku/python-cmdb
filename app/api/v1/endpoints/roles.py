from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.api.deps import get_db, get_current_active_user
from app.services.role import RoleService
from app.services.casbin_service import CasbinService
from app.schemas.role import CasbinRole, CasbinRoleList, RoleAssignRequest
from app.schemas.user import User

router = APIRouter()

async def check_admin_permission(current_user: User) -> bool:
    """检查用户是否有admin权限"""
    return current_user.is_superuser

# ==================== 角色管理 API (仅admin) ====================

@router.get("/roles/", response_model=CasbinRoleList, summary="List Roles", description="获取所有角色列表 - 仅admin")
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有角色列表"""
    if not await check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    role_service = RoleService(db)
    roles = await role_service.get_all_roles()
    
    # 应用分页
    total = len(roles)
    paginated_roles = roles[skip:skip + limit]
    
    return CasbinRoleList(roles=paginated_roles, count=total)

@router.post("/roles/", response_model=CasbinRole, summary="Create Role", description="创建新角色 - 仅admin")
async def create_role(
    role_name: str,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新角色"""
    if not await check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        role_service = RoleService(db)
        role = await role_service.create_role(role_name, description)
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/roles/{role_name}", response_model=CasbinRole, summary="Get Role", description="获取角色详情 - 仅admin")
async def get_role(
    role_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取角色详情"""
    if not await check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    role_service = RoleService(db)
    try:
        role = await role_service.get_role_by_name(role_name)
        return role
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

# ==================== 用户角色分配 API (仅admin) ====================

@router.post("/users/{username}/roles/", summary="Assign Role To User", description="给用户分配角色 - 仅admin")
async def assign_role_to_user(
    username: str,
    role_assign: RoleAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """给用户分配角色"""
    if not await check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    # 确保用户名一致
    if username != role_assign.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不匹配"
        )
    
    role_service = RoleService(db)
    success = await role_service.assign_role_to_user(username, role_assign.role)
    
    if success:
        return {"message": f"成功为用户 {username} 分配角色 {role_assign.role}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色分配失败"
        )

@router.delete("/users/{username}/roles/{role_name}", summary="Remove Role From User", description="从用户中移除角色 - 仅admin")
async def remove_role_from_user(
    username: str,
    role_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """从用户中移除角色"""
    if not await check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    role_service = RoleService(db)
    success = await role_service.remove_role_from_user(username, role_name)
    
    if success:
        return {"message": f"成功从用户 {username} 移除角色 {role_name}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色移除失败"
        )

@router.get("/users/{username}/roles/", summary="Get User Roles", description="获取用户的所有角色 - 仅admin")
async def get_user_roles(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的所有角色"""
    if not await check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    role_service = RoleService(db)
    roles = await role_service.get_user_roles(username)
    
    return {
        "username": username,
        "roles": roles,
        "count": len(roles)
    } 