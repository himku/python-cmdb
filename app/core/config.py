# Import required modules
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


## Configurations for the application
class Settings(BaseSettings):
    # Basic application settings
    PROJECT_NAME: str = "CMDB"  # Name of the project
    VERSION: str = "1.0.0"      # Current version
    API_V1_STR: str = "/api/v1" # API version prefix
    
    # Database connection settings
    MYSQL_HOST: str             # MySQL server hostname
    MYSQL_USER: str             # MySQL username
    MYSQL_PASSWORD: str         # MySQL password
    MYSQL_DB: str              # MySQL database name
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # Full database connection string
    
    # JWT authentication settings
    SECRET_KEY: str            # Secret key for JWT token signing
    ALGORITHM: str = "HS256"   # Algorithm used for JWT token
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time in minutes
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: list[str] = ["*"]  # List of allowed origins, "*" allows all
    
    class Config:
        case_sensitive = True   # Make settings case sensitive
        env_file = ".env"      # Load settings from .env file

    def __init__(self, **kwargs):
        """
        Initialize Settings with environment variables.
        Constructs database URI if not explicitly provided.
        """
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}/{self.MYSQL_DB}"
            )

@lru_cache()
def get_settings() -> Settings:
    """
    Create and return a cached instance of Settings.
    Uses lru_cache to prevent reading environment variables multiple times.
    """
    return Settings() 