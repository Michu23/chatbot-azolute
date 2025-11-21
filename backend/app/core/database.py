from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator

from app.core.config import settings

# Convert DATABASE_URL to async if needed
database_url = settings.DATABASE_URL

# Handle different database types
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

# Determine if using SQLite
is_sqlite = "sqlite" in database_url

# Create async engine with appropriate settings
engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
    "future": True,
}

# SQLite needs special handling for async
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(database_url, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


# Dependency for getting database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Initialize database
async def init_db():
    # Try to enable pgvector extension (PostgreSQL only)
    if not is_sqlite:
        try:
            async with engine.begin() as conn:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception as e:
            print(f"Note: pgvector extension not available. RAG features will be disabled. Error: {e}")

    # For SQLite in development, create tables directly
    if is_sqlite:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("SQLite tables created successfully")

    # Note: For PostgreSQL, tables should be created using Alembic migrations
    # Run: alembic upgrade head
