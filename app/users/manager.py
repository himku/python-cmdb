from fastapi import Depends
from fastapi_users.manager import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.users.models import User
from app.database.session import SessionLocal
from app.core.config import get_settings
from typing import AsyncGenerator

settings = get_settings()

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    @staticmethod
    def parse_id(user_id: int) -> int:
        return user_id

    async def on_after_register(self, user: User, request=None):
        pass

async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    async with SessionLocal() as session:
        yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
