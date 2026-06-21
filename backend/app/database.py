from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),  # 仅开发模式打印SQL
    pool_pre_ping=True,    # 连接前检测存活（解决 Celery asyncio.run() 跨事件循环连接残留）
    pool_recycle=1800,     # 30 分钟后回收连接，防止僵尸连接积累
)

# 创建Session工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 所有Model的基类
class Base(DeclarativeBase):
    pass

# 获取数据库Session的依赖函数
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise