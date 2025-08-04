from fastapi import APIRouter
from app.api.v1.endpoints import users, roles, casbin

api_router = APIRouter()

# 用户相关API
api_router.include_router(users.router, prefix="/users", tags=["users"])

# 系统管理API（需要admin权限）
api_router.include_router(roles.router, prefix="/admin", tags=["admin", "system"])

# Casbin 权限管理API（需要admin权限）
api_router.include_router(casbin.router, prefix="/admin/casbin", tags=["admin", "casbin", "permission"]) 