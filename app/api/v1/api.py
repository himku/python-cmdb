from fastapi import APIRouter
from app.api.v1.endpoints import users, roles, menus

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/admin", tags=["admin", "roles", "permissions"])
api_router.include_router(menus.router, tags=["menus"]) 