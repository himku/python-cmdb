import sys
import uuid
import os
from loguru import logger
from datetime import datetime

def setup_logging():
    """设置应用日志系统"""
    # 移除默认处理器
    logger.remove()
    
    # 创建logs目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 控制台输出 - 彩色格式
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="DEBUG",
        enqueue=True,
        colorize=True
    )
    
    # 文件输出 - 所有级别
    logger.add(
        f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        enqueue=True
    )
    
    # 错误日志单独文件
    logger.add(
        f"{log_dir}/error_{datetime.now().strftime('%Y%m%d')}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        enqueue=True
    )
    
    return logger

# 创建应用级别的logger实例
app_logger = setup_logging()

def get_logger(name: str = "app"):
    """获取带名称的logger"""
    return logger.bind(name=name)

# 请求ID上下文
request_id_var = None

def set_request_id():
    """为请求设置唯一ID"""
    global request_id_var
    request_id_var = str(uuid.uuid4())[:8]
    return request_id_var

def get_request_id():
    """获取当前请求ID"""
    return request_id_var or "unknown"

def log_request(method: str, path: str, status_code: int, duration: float = None):
    """记录HTTP请求日志"""
    duration_str = f" in {duration:.3f}s" if duration else ""
    logger.info(f"🌐 {method} {path} -> {status_code}{duration_str} [req:{get_request_id()}]")

def log_auth(username: str, action: str, success: bool = True):
    """记录认证相关日志"""
    status = "✅" if success else "❌"
    logger.info(f"🔐 {status} Auth: {username} {action} [req:{get_request_id()}]")

def log_permission(username: str, resource: str, action: str, granted: bool):
    """记录权限检查日志"""
    status = "✅" if granted else "❌"
    logger.info(f"🛡️  {status} Permission: {username} {action} {resource} [req:{get_request_id()}]")

def log_casbin(action: str, details: str):
    """记录Casbin操作日志"""
    logger.info(f"⚡ Casbin: {action} - {details} [req:{get_request_id()}]")

def log_database(operation: str, table: str, details: str = ""):
    """记录数据库操作日志"""
    logger.debug(f"💾 DB: {operation} {table} {details} [req:{get_request_id()}]")

def log_error(error: Exception, context: str = ""):
    """记录错误日志"""
    logger.error(f"💥 Error in {context}: {type(error).__name__}: {str(error)} [req:{get_request_id()}]")

def log_api_call(endpoint: str, method: str, user: str = "anonymous"):
    """记录API调用日志"""
    logger.info(f"📡 API: {method} {endpoint} by {user} [req:{get_request_id()}]") 