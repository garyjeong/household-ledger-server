"""
Database Configuration
SQLAlchemy 2.0+ with Async
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings


# Base class for models
class Base(DeclarativeBase):
    pass


# Create async engine
engine = create_async_engine(
    settings.database_url.replace("mysql+pymysql", "mysql+aiomysql"),
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for getting database session
async def get_session() -> AsyncSession:
    """Get async database session"""
    async with async_session_maker() as session:
        yield session


# Legacy sync engine (for Alembic)
sync_engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
)

sync_session_maker = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
)

