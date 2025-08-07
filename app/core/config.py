# 导入所需模块
from pydantic_settings import BaseSettings
from typing import Optional, List, Union
from functools import lru_cache

## 应用程序配置
class Settings(BaseSettings):
    # 基本应用设置
    PROJECT_NAME: str = "CMDB"  # 项目名称
    VERSION: str = "1.0.0"      # 当前版本
    API_V1_STR: str = "/api/v1" # API 版本前缀
    
    # 数据库连接设置
    MYSQL_HOST: str             # MySQL 服务器主机名
    MYSQL_USER: str             # MySQL 用户名
    MYSQL_PASSWORD: str         # MySQL 密码
    MYSQL_DB: str               # MySQL 数据库名
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # 完整数据库连接字符串
    
    # Redis 连接设置
    REDIS_HOST: str = "localhost"    # Redis 服务器主机名
    REDIS_PORT: int = 6379           # Redis 服务器端口
    REDIS_PASSWORD: Optional[str] = None  # Redis 密码（可选）
    REDIS_DB: int = 0                # Redis 数据库编号
    REDIS_URL: Optional[str] = None  # 完整 Redis 连接字符串
    
    # JWT 认证设置
    SECRET_KEY: str                  # JWT 签名密钥
    ALGORITHM: str = "HS256"         # JWT 使用的算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token 过期时间（分钟）
    
    # CORS 配置 - 跨域资源共享设置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",     # React 开发服务器
        "http://localhost:8080",     # Vue 开发服务器
        "http://localhost:5173",     # Vite 开发服务器
        "http://localhost:4200",     # Angular 开发服务器
        "http://localhost:8000",     # Django/其他框架
        "http://localhost:9000",     # 其他常用端口
        "http://localhost:9527",     # Vue Admin Template
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:9000",
        "http://127.0.0.1:9527",
    ]
    
    # CORS 高级配置
    CORS_ALLOW_CREDENTIALS: bool = True           # 是否允许携带认证信息
    CORS_ALLOW_METHODS: List[str] = [             # 允许的HTTP方法
        "GET", "POST", "PUT", "DELETE", 
        "OPTIONS", "HEAD", "PATCH"
    ]
    CORS_ALLOW_HEADERS: List[str] = [             # 允许的请求头
        "Accept", 
        "Accept-Language", 
        "Content-Language", 
        "Content-Type", 
        "Authorization", 
        "X-Requested-With",
        "X-CSRF-Token", 
        "X-Request-ID",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ]
    CORS_EXPOSE_HEADERS: List[str] = [            # 暴露给客户端的响应头
        "X-Request-ID", 
        "X-Response-Time",
        "Content-Length",
        "Content-Type"
    ]
    CORS_MAX_AGE: int = 86400                     # 预检请求缓存时间（秒）
    
    # 环境模式
    ENVIRONMENT: str = "development"              # 环境模式: development, production, testing
    
    class Config:
        case_sensitive = True   # 设置区分大小写
        env_file = ".env"      # 从 .env 文件加载配置

    def __init__(self, **kwargs):
        """
        使用环境变量初始化 Settings。
        如果未显式提供，则自动构建数据库 URI 和 Redis URL。
        """
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}/{self.MYSQL_DB}"
            )
        
        if not self.REDIS_URL:
            if self.REDIS_PASSWORD:
                self.REDIS_URL = (
                    f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:"
                    f"{self.REDIS_PORT}/{self.REDIS_DB}"
                )
            else:
                self.REDIS_URL = (
                    f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
                )
        
        # 根据环境调整CORS设置
        if self.ENVIRONMENT == "production":
            # 生产环境使用更严格的CORS设置
            if "*" in self.BACKEND_CORS_ORIGINS:
                self.BACKEND_CORS_ORIGINS = [
                    "https://yourdomain.com",    # 替换为实际的生产域名
                    "https://admin.yourdomain.com"
                ]
        elif self.ENVIRONMENT == "development":
            # 开发环境添加通配符支持
            if "*" not in self.BACKEND_CORS_ORIGINS:
                self.BACKEND_CORS_ORIGINS.append("*")
            # 清理空字符串
            self.BACKEND_CORS_ORIGINS = [origin for origin in self.BACKEND_CORS_ORIGINS if origin]

@lru_cache()
def get_settings():
    """
    使用 LRU 缓存获取设置实例，确保单例模式。
    """
    return Settings()
