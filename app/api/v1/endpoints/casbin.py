from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user
from app.services.casbin_service import CasbinService
from app.schemas.user import User

router = APIRouter()

# 检查超级管理员权限
async def require_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """确保当前用户是超级管理员"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以执行此操作"
        )
    return current_user

# Pydantic 模型
class PolicyRequest(BaseModel):
    role: str
    obj: str
    act: str

class RoleAssignRequest(BaseModel):
    username: str
    role: str

class PermissionCheckRequest(BaseModel):
    username: str
    obj: str
    act: str

# ==================== 策略管理 API (仅超级管理员) ====================

@router.get("/policies/")
async def list_policies(
    current_user: User = Depends(require_superuser)
):
    """获取所有策略 - 仅超级管理员"""
    policies = CasbinService.get_all_policies()
    
    return JSONResponse(content={
        "policies": policies,
        "count": len(policies)
    })

@router.post("/policies/")
async def add_policy(
    policy: PolicyRequest,
    current_user: User = Depends(require_superuser)
):
    """添加策略 - 仅超级管理员"""
    success = CasbinService.add_policy(policy.role, policy.obj, policy.act)
    
    if success:
        return JSONResponse(content={"message": "策略添加成功"})
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="策略添加失败或已存在"
        )

@router.delete("/policies/")
async def remove_policy(
    policy: PolicyRequest,
    current_user: User = Depends(require_superuser)
):
    """删除策略 - 仅超级管理员"""
    success = CasbinService.remove_policy(policy.role, policy.obj, policy.act)
    
    if success:
        return JSONResponse(content={"message": "策略删除成功"})
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="策略删除失败或不存在"
        )

# ==================== 角色管理 API (仅超级管理员) ====================

@router.get("/roles/")
async def list_all_roles(
    current_user: User = Depends(require_superuser)
):
    """获取所有角色 - 仅超级管理员"""
    roles = CasbinService.get_all_roles()
    
    return JSONResponse(content={
        "roles": roles,
        "count": len(roles)
    })

@router.post("/users/roles/")
async def assign_role_to_user(
    assignment: RoleAssignRequest,
    current_user: User = Depends(require_superuser)
):
    """为用户分配角色 - 仅超级管理员"""
    success = CasbinService.add_role_for_user(assignment.username, assignment.role)
    
    if success:
        return JSONResponse(content={"message": f"成功为用户 {assignment.username} 分配角色 {assignment.role}"})
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色分配失败"
        )

@router.delete("/users/roles/")
async def remove_role_from_user(
    assignment: RoleAssignRequest,
    current_user: User = Depends(require_superuser)
):
    """从用户移除角色 - 仅超级管理员"""
    success = CasbinService.delete_role_for_user(assignment.username, assignment.role)
    
    if success:
        return JSONResponse(content={"message": f"成功从用户 {assignment.username} 移除角色 {assignment.role}"})
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色移除失败"
        )

@router.get("/users/{username}/roles/")
async def get_user_roles(
    username: str,
    current_user: User = Depends(require_superuser)
):
    """获取用户的所有角色 - 仅超级管理员"""
    roles = CasbinService.get_roles_for_user(username)
    
    return JSONResponse(content={
        "username": username,
        "roles": roles,
        "count": len(roles)
    })

@router.get("/roles/{role}/users/")
async def get_role_users(
    role: str,
    current_user: User = Depends(require_superuser)
):
    """获取拥有指定角色的所有用户 - 仅超级管理员"""
    users = CasbinService.get_users_for_role(role)
    
    return JSONResponse(content={
        "role": role,
        "users": users,
        "count": len(users)
    })

# ==================== 权限检查 API (仅超级管理员) ====================

@router.post("/check/")
async def check_permission(
    check: PermissionCheckRequest,
    current_user: User = Depends(require_superuser)
):
    """检查用户权限 - 仅超级管理员"""
    has_permission = CasbinService.check_permission(check.username, check.obj, check.act)
    
    return JSONResponse(content={
        "username": check.username,
        "obj": check.obj,
        "act": check.act,
        "has_permission": has_permission
    })

@router.get("/users/{username}/permissions/")
async def get_user_permissions(
    username: str,
    current_user: User = Depends(require_superuser)
):
    """获取用户的所有权限 - 仅超级管理员"""
    permissions = CasbinService.get_permissions_for_user(username)
    
    return JSONResponse(content={
        "username": username,
        "permissions": permissions,
        "count": len(permissions)
    })

# ==================== 同步和管理 API (仅超级管理员) ====================

@router.post("/sync/", summary="Sync From Database", description="从数据库同步用户角色到 Casbin - 仅超级管理员")
async def sync_from_database(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """从数据库同步用户角色到 Casbin"""
    # 检查是否为超级管理员
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    
    # 现在使用RoleService进行同步
    from app.services.role import RoleService
    role_service = RoleService(db)
    synced_count = await role_service.sync_superusers_to_casbin()
    
    return {
        "message": "同步完成",
        "synced_users": synced_count
    }

@router.post("/initialize/")
async def initialize_default_policies(
    current_user: User = Depends(require_superuser)
):
    """初始化默认策略 - 仅超级管理员"""
    try:
        CasbinService.initialize_default_policies()
        return JSONResponse(content={"message": "默认策略初始化成功"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化失败: {str(e)}"
        )

@router.post("/reload/")
async def reload_policies(
    current_user: User = Depends(require_superuser)
):
    """重新加载策略 - 仅超级管理员"""
    try:
        CasbinService.load_policy()
        return JSONResponse(content={"message": "策略重新加载成功"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新加载失败: {str(e)}"
        ) 