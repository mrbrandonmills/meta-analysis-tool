"""Async database session configuration with advanced pooling and transaction management."""

from typing import AsyncGenerator
from contextlib import asynccontextmanager

import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import event

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Convert database URL to async version
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
if async_database_url.startswith("sqlite"):
    async_database_url = async_database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Determine pool settings based on database type
is_sqlite = "sqlite" in async_database_url
# For async engines, always use NullPool (async engines manage their own pooling)
pool_class = NullPool
pool_kwargs = {}  # NullPool doesn't accept pool_size, max_overflow, etc.

# Create async engine with connection pooling
async_engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before using
    poolclass=pool_class,
    **pool_kwargs,
)

# Create async session factory
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Event listeners for connection tracking
@event.listens_for(async_engine.sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections."""
    logger.debug("Async database connection established")


@event.listens_for(async_engine.sync_engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections."""
    logger.debug("Async database connection closed")


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database sessions.

    Automatically handles:
    - Session creation and cleanup
    - Transaction commit on success
    - Rollback on error

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def async_transaction(session: AsyncSession):
    """
    Explicit transaction context manager for complex operations.

    Usage:
        async with async_transaction(db):
            user = User(email="test@example.com")
            db.add(user)
            # Automatically commits on success, rolls back on error
    """
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def init_async_db() -> None:
    """
    Initialize async database - create all tables.

    Should be called during application startup.
    """
    from app.db.base import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Async database tables created successfully")


async def close_async_db() -> None:
    """
    Close async database connections.

    Should be called during application shutdown.
    """
    await async_engine.dispose()
    logger.info("Async database connections closed")
