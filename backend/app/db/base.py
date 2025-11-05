"""Database base configuration with sync session management."""

from typing import Generator
from contextlib import contextmanager

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Determine pool settings based on database type
is_sqlite = "sqlite" in settings.database_url
pool_class = NullPool if is_sqlite else QueuePool
pool_kwargs = {} if is_sqlite else {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 3600,
    "pool_timeout": 30,
}

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    poolclass=pool_class,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    **pool_kwargs,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


# Event listeners for connection tracking
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections."""
    logger.debug("Sync database connection established")


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections."""
    logger.debug("Sync database connection closed")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for sync database sessions.

    Automatically handles:
    - Session creation and cleanup
    - Transaction commit on success
    - Rollback on error

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def db_transaction(session: Session):
    """
    Explicit transaction context manager for complex operations.

    Usage:
        with db_transaction(db):
            user = User(email="test@example.com")
            db.add(user)
            # Automatically commits on success, rolls back on error
    """
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


def init_db() -> None:
    """
    Initialize sync database - create all tables.

    Should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Sync database tables created successfully")


def close_db() -> None:
    """
    Close sync database connections.

    Should be called during application shutdown.
    """
    engine.dispose()
    logger.info("Sync database connections closed")
