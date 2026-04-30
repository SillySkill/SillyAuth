"""
后台管理系统 - 异步数据库连接管理
支持PostgreSQL和MySQL
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # postgresql or mysql

if DB_TYPE == 'postgresql':
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://sillyAdmin:Jcoding2026@47.96.133.238:5432/sillymd'
    )
else:
    DATABASE_URL = os.getenv(
        'DATABASE_URL_MYSQL',
        'mysql+aiomysql://root:password@localhost:3306/jc_ai_activity'
    )

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 设置为True可查看SQL日志
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 检查连接有效性
    pool_recycle=3600,   # 1小时回收连接
)

# 创建异步Session工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """
    获取数据库Session

    Usage:
        async for db in get_db():
            result = await db.execute(select(User))
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session():
    """
    获取单个数据库Session（需要手动关闭）

    Usage:
        db = await get_db_session()
        try:
            result = await db.execute(select(User))
            ...
        finally:
            await db.close()
    """
    return async_session_maker()
