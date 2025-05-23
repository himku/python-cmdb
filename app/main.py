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
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
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


