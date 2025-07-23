from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database import init_db
from app.api.v1.api import api_router
import uuid
from loguru import logger

settings = get_settings()
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and create admin user
    try:
        logger.info(f"Starting database initialization {settings.MYSQL_HOST}")
        init_db()
        logger.info(f"Database initialization completed successfully {settings.MYSQL_HOST}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    yield
    logger.info(f"Shutting down {settings.MYSQL_HOST}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="一个基于 FastAPI 的现代化配置管理数据库系统，支持资产管理、用户认证、权限控制等功能。\n\n"
                "访问 [Swagger UI](/docs) 或 [ReDoc](/redoc) 查看完整 API 文档。",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    terms_of_service="https://github.com/himku/python-cmdb",
    contact={
        "name": "admin",
        "url": "https://github.com/himku/python-cmdb",
        "email": "admin@qq.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    with logger.contextualize(uuid=request_id):
        response = await call_next(request)
    return response

@app.get("/")
async def root():
    logger.info("Welcome to CMDB API")
    return {"message": "Welcome to CMDB API"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    Returns a simple JSON response indicating the service is running.
    """
    return {"status": "ok", "message": "CMDB API is running smoothly."}