from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from app.config import get_settings

from sqlalchemy.pool import StaticPool

# Retrieve application settings
settings = get_settings()

# Build engine kwargs based on database backend.
# SQLite does not support pool_size / max_overflow — use StaticPool instead.
_engine_kwargs: dict = {"echo": settings.DEBUG}

if "sqlite" in settings.DATABASE_URL:
    _engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
else:
    _engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

# Configure the async session factory
# expire_on_commit=False prevents issues where accessed attributes would emit a lazy load
# after the transaction has ended in async contexts.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session per request.
    Handles transaction management automatically (commits on success, rolls back on error).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

