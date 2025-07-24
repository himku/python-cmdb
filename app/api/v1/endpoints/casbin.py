from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from app.services.casbin_enforcer import add_policy, remove_policy, get_policies, check_permission, get_user_policies
from app.api.deps import get_current_user

router = APIRouter()

class PolicyIn(BaseModel):
    sub: str
    obj: str
    act: str

@router.get(
    "/policies",
    summary="获取用户的权限策略（仅限admin）",
    description="""
仅 admin 用户可访问本接口。  
用于查询指定用户名的所有 Casbin 权限策略（即该用户拥有的所有资源-操作权限）。

- 需要在请求头中携带有效的 JWT Token（登录后获取）。
- 非 admin 用户访问将返回 403 无权限。

**用法示例：**

- 请求：
    GET /api/v1/casbin/policies?username=admin
    Header: Authorization: Bearer <token>

- 返回：
    {
      "policies": [
        ["admin", "*", "*"]
      ]
    }
"""
)
def list_user_policies(
    username: str = Query(..., description="用户名"),
    current_user=Depends(get_current_user)
):
    """
    获取指定用户的所有权限策略，仅 admin 可用。
    """
    # 只有 admin 用户才能访问
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="无权限访问")
    return {"policies": get_user_policies(username)}

@router.post("/policy", summary="添加权限策略")
def add_policy_api(policy: PolicyIn):
    ok = add_policy(policy.sub, policy.obj, policy.act)
    if not ok:
        raise HTTPException(status_code=400, detail="策略已存在")
    return {"msg": "添加成功"}

@router.delete("/policy", summary="删除权限策略")
def remove_policy_api(policy: PolicyIn):
    ok = remove_policy(policy.sub, policy.obj, policy.act)
    if not ok:
        raise HTTPException(status_code=404, detail="策略不存在")
    return {"msg": "删除成功"}

class PermissionCheckIn(BaseModel):
    sub: str
    obj: str
    act: str

@router.post("/permission/check", summary="权限校验")
def check_permission_api(data: PermissionCheckIn):
    ok = check_permission(data.sub, data.obj, data.act)
    return {"allowed": ok}
