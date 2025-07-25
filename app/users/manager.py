from fastapi import Depends
from fastapi_users.manager import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.users.models import User
from app.database.session import SessionLocal
from typing import AsyncGenerator

SECRET = "CHANGE_ME"  # 可用 settings.SECRET_KEY

class UserManager(BaseUserManager[User, str]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request=None):
        pass

async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    async with SessionLocal() as session:
        yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
