import os
from app import settings

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, registry

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_address = os.getenv("DB_ADDRESS")
db_port = os.getenv("DB_PORT")
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_address}:{db_port}/{settings.app_name}"

engine = create_async_engine(DATABASE_URL, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

mapper_registry = registry()


async def get_db():
    async with async_session() as session:
        yield session


async def get_db_cm():
    async with async_session() as session:
        async with session.begin():
            yield session
