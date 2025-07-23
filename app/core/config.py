# 导入所需模块
from pydantic_settings import BaseSettings
from typing import Optional
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
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: list[str] = ["*"]  # 允许的来源列表，"*" 表示全部允许
    
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

@lru_cache()
def get_settings() -> Settings:
    """
    创建并返回 Settings 的缓存实例。
    使用 lru_cache 防止多次读取环境变量。
    """
    return Settings()
