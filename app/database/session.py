from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI.replace("mysql+pymysql://", "mysql+aiomysql://")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
