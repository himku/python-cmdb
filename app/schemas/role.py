from pydantic import BaseModel
from typing import List, Optional

# Casbin角色相关的数据模型

class CasbinRole(BaseModel):
    """Casbin角色信息"""
    name: str
    description: Optional[str] = None
    users: List[str] = []  # 拥有此角色的用户列表
    
class CasbinPolicy(BaseModel):
    """Casbin策略信息"""
    role: str
    resource: str  # 资源路径
    action: str    # 操作类型
    
class RoleAssignRequest(BaseModel):
    """角色分配请求"""
    username: str
    role: str
    
class PolicyRequest(BaseModel):
    """策略请求"""
    role: str
    obj: str   # 对象/资源
    act: str   # 动作/操作
    
class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    username: str
    obj: str   # 对象/资源
    act: str   # 动作/操作

class CasbinRoleList(BaseModel):
    """角色列表响应"""
    roles: List[CasbinRole]
    count: int
    
class CasbinPolicyList(BaseModel):
    """策略列表响应"""
    policies: List[List[str]]  # Casbin策略格式 [role, resource, action]
    count: int 