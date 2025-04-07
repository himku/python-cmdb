import sys
import uuid
from loguru import logger

def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Add console handler with UUID
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="INFO",
        enqueue=True
    )
    
    return logger 