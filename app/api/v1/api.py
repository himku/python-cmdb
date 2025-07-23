from fastapi import APIRouter
from app.api.v1.endpoints import auth, casbin_model, casbin, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(casbin.router, prefix="/casbin", tags=["casbin"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
