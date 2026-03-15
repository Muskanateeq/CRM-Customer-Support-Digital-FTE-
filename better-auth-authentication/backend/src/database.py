"""
Database Connection Module

Manages database connections and sessions using SQLModel and asyncpg.
Provides session management for FastAPI dependency injection.
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import ssl

from src.config import settings

# Create synchronous engine for Alembic migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create async engine for FastAPI application
# Remove sslmode parameter from URL as asyncpg doesn't support it
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
# Remove sslmode parameter if present
async_database_url = async_database_url.replace("?sslmode=require", "").replace("&sslmode=require", "")

# Create SSL context for asyncpg
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async_engine = create_async_engine(
    async_database_url,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "ssl": ssl_context,  # asyncpg uses ssl parameter, not sslmode
    }
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def create_db_and_tables():
    """Create all database tables (for development only)"""
    SQLModel.metadata.create_all(sync_engine)


async def get_session() -> AsyncSession:
    """
    Dependency function to get database session.

    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
