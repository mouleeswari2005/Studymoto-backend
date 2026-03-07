"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from urllib.parse import urlparse

# Determine if SSL is required
# Check if it's a cloud database (not localhost) or if URL contains SSL indicators
db_url = settings.DATABASE_URL
parsed = urlparse(db_url)
is_cloud_db = parsed.hostname and parsed.hostname not in ('localhost', '127.0.0.1', '::1')

# Configure connect_args for asyncpg SSL
# Cloud databases (like Aiven) typically require SSL
connect_args = {}
if is_cloud_db:
    # asyncpg uses 'ssl' parameter with value 'require' for required SSL
    connect_args['ssl'] = 'require'

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args if connect_args else {},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

