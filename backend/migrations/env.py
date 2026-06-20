from logging.config import fileConfig

import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import User, Site, Page, Revision, Rating

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Allow DATABASE_URL environment variable to override alembic.ini's sqlalchemy.url
# This is used in Docker deployments where the DB hostname differs from localhost.
# NOTE: We intentionally avoid config.set_main_option() because ConfigParser would
# interpolate %-encoded characters in the URL (e.g. %40 for @ in passwords).
database_url = os.getenv("DATABASE_URL")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = database_url or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    这是实际执行迁移的同步包裹函数
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 如果你有其他配置可以写在这里
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """
    创建一个异步引擎并运行迁移
    """
    # 获取配置 section 并注入 database_url（绕过 ConfigParser 的 % 插值问题）
    section = config.get_section(config.config_ini_section, {})
    if database_url:
        section["sqlalchemy.url"] = database_url
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # 使用 run_sync 将异步连接桥接到同步的 Alembic 迁移环境中
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # 通过 asyncio 启动异步任务
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
