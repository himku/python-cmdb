from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.casbin_enforcer import add_policy, remove_policy, get_policies, check_permission

router = APIRouter()

class PolicyIn(BaseModel):
    sub: str
    obj: str
    act: str

@router.get("/policies", summary="获取所有权限策略")
def list_policies():
    return {"policies": get_policies()}

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
