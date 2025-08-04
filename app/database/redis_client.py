import redis
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


def get_redis_pool() -> redis.ConnectionPool:
    """
    Create and return Redis connection pool.
    Uses connection pooling for better performance.
    """
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            retry_on_timeout=True,
            decode_responses=True
        )
    return redis_pool


def get_redis_client() -> redis.Redis:
    """
    Create and return Redis client instance.
    Uses connection pool for efficient connection management.
    """
    global redis_client
    if redis_client is None:
        pool = get_redis_pool()
        redis_client = redis.Redis(connection_pool=pool)
    return redis_client


def get_redis() -> redis.Redis:
    """
    Dependency function to get Redis client.
    Can be used with FastAPI's dependency injection.
    """
    return get_redis_client()


async def ping_redis() -> bool:
    """
    Test Redis connection.
    Returns True if connection is successful, False otherwise.
    """
    try:
        client = get_redis_client()
        return client.ping()
    except Exception:
        return False


def close_redis_connection():
    """
    Close Redis connection pool.
    Should be called when shutting down the application.
    """
    global redis_pool, redis_client
    if redis_client:
        redis_client.close()
        redis_client = None
    if redis_pool:
        redis_pool.disconnect()
        redis_pool = None
