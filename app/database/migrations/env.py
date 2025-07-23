from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# 允许 alembic 直接导入 app 目录下的模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.database.session import Base
from app.core.config import get_settings

# 读取 alembic.ini 配置
config = context.config

# 读取 .env 环境变量
settings = get_settings()

# 动态设置数据库连接
config.set_main_option('sqlalchemy.url', settings.SQLALCHEMY_DATABASE_URI)

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
