from __future__ import annotations
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, Float, DateTime, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from core.config import get_db_config

logger = logging.getLogger(__name__)

Base = declarative_base()


class ConfigData(Base):
    """通用配置数据模型"""
    __tablename__ = "config_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    data = Column(JSON, nullable=False, default=dict)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "data": self.data,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConfigDataService:
    """配置数据服务"""

    def __init__(self):
        self._engine = None
        self._session_factory = None

    def _get_engine(self):
        if self._engine is None:
            db_config = get_db_config()
            database_url = (
                f"postgresql+asyncpg://{db_config.user}:{db_config.password}"
                f"@{db_config.host}:{db_config.port}/{db_config.database}"
            )
            self._engine = create_async_engine(database_url, echo=False)
            self._session_factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
        return self._engine, self._session_factory

    async def list_by_category(self, category: str) -> Tuple[List[Dict[str, Any]], int]:
        """按分类获取所有数据"""
        engine, session_factory = self._get_engine()

        async with session_factory() as session:
            from sqlalchemy import select, func

            # 查询总数
            count_query = select(func.count()).select_from(ConfigData).where(
                ConfigData.category == category
            )
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # 查询列表
            query = select(ConfigData).where(ConfigData.category == category).order_by(ConfigData.id)
            result = await session.execute(query)
            items = result.scalars().all()

            return [item.to_dict() for item in items], total

    async def get_by_name(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        """按分类和名称获取数据"""
        engine, session_factory = self._get_engine()

        async with session_factory() as session:
            from sqlalchemy import select

            query = select(ConfigData).where(
                ConfigData.category == category,
                ConfigData.name == name
            )
            result = await session.execute(query)
            item = result.scalar_one_or_none()

            return item.to_dict() if item else None

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据"""
        engine, session_factory = self._get_engine()

        async with session_factory() as session:
            config_data = ConfigData(
                category=data.get("category"),
                name=data.get("name"),
                data=data.get("data", {}),
                position_x=data.get("position_x"),
                position_y=data.get("position_y"),
            )
            session.add(config_data)
            await session.commit()
            await session.refresh(config_data)
            return config_data.to_dict()

    async def update(self, category: str, name: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新数据"""
        engine, session_factory = self._get_engine()

        async with session_factory() as session:
            from sqlalchemy import select

            query = select(ConfigData).where(
                ConfigData.category == category,
                ConfigData.name == name
            )
            result = await session.execute(query)
            config_data = result.scalar_one_or_none()

            if not config_data:
                return None

            for key, value in update_data.items():
                if key == "data":
                    config_data.data = value
                elif key == "position_x":
                    config_data.position_x = value
                elif key == "position_y":
                    config_data.position_y = value
                elif key == "name":
                    config_data.name = value

            config_data.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(config_data)
            return config_data.to_dict()

    async def delete(self, category: str, name: str) -> bool:
        """删除数据"""
        engine, session_factory = self._get_engine()

        async with session_factory() as session:
            from sqlalchemy import select, delete

            query = select(ConfigData).where(
                ConfigData.category == category,
                ConfigData.name == name
            )
            result = await session.execute(query)
            config_data = result.scalar_one_or_none()

            if not config_data:
                return False

            await session.delete(config_data)
            await session.commit()
            return True

    async def batch_update(self, category: str, items: List[Dict[str, Any]]) -> int:
        """批量更新数据"""
        engine, session_factory = self._get_engine()

        updated_count = 0
        async with session_factory() as session:
            from sqlalchemy import select

            for item in items:
                name = item.get("name")
                if not name:
                    continue

                query = select(ConfigData).where(
                    ConfigData.category == category,
                    ConfigData.name == name
                )
                result = await session.execute(query)
                config_data = result.scalar_one_or_none()

                if config_data:
                    if "position_x" in item:
                        config_data.position_x = item["position_x"]
                    if "position_y" in item:
                        config_data.position_y = item["position_y"]
                    if "data" in item:
                        config_data.data = item["data"]
                    config_data.updated_at = datetime.utcnow()
                    updated_count += 1

            await session.commit()
            return updated_count

    async def init_table(self):
        """初始化数据库表"""
        db_config = get_db_config()
        # 使用同步连接来创建表
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        sync_url = (
            f"postgresql://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        engine = create_engine(sync_url)

        # 创建表
        Base.metadata.create_all(engine)
        logger.info("config_data 表创建成功")


# 全局服务实例
config_data_service = ConfigDataService()


# 同步版本服务（用于种子数据导入）
class SyncConfigDataService:
    """同步版本配置数据服务"""

    def __init__(self):
        self._engine = None
        self._session_factory = None

    def _get_connection(self):
        if self._engine is None:
            db_config = get_db_config()
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            sync_url = (
                f"postgresql://{db_config.user}:{db_config.password}"
                f"@{db_config.host}:{db_config.port}/{db_config.database}"
            )
            self._engine = create_engine(sync_url)
            self._session_factory = sessionmaker(bind=self._engine)
        return self._engine, self._session_factory

    def upsert(self, category: str, name: str, data: Dict[str, Any],
               position_x: float = None, position_y: float = None):
        """插入或更新数据"""
        engine, session_factory = self._get_connection()

        with session_factory() as session:
            from sqlalchemy import select

            # 查询是否存在
            query = select(ConfigData).where(
                ConfigData.category == category,
                ConfigData.name == name
            )
            result = session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                # 更新
                existing.data = data
                existing.position_x = position_x
                existing.position_y = position_y
                existing.updated_at = datetime.utcnow()
            else:
                # 创建
                config_data = ConfigData(
                    category=category,
                    name=name,
                    data=data,
                    position_x=position_x,
                    position_y=position_y,
                )
                session.add(config_data)

            session.commit()
            return True

    def init_table(self):
        """初始化数据库表"""
        engine, _ = self._get_connection()
        Base.metadata.create_all(engine)
        logger.info("config_data 表创建成功")


sync_config_data_service = SyncConfigDataService()
