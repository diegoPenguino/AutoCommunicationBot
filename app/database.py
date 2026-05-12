from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime, timezone
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create the async engine
# Note: we need to handle the case where settings.database_url might be empty or wrong in test environments
try:
    engine = create_async_engine(settings.database_url, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
except Exception as e:
    logger.error(f"Could not create database engine: {e}")
    engine = None
    AsyncSessionLocal = None

Base = declarative_base()

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

async def init_db():
    if engine:
        async with engine.begin() as conn:
            # Create all tables. In a production environment, you should use Alembic.
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized.")
    else:
        logger.warning("Database engine is not configured.")

async def get_db():
    if not AsyncSessionLocal:
        yield None
        return
        
    async with AsyncSessionLocal() as session:
        yield session
