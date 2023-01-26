import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, registry

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/fastapi"
MONGO_DATABASE_URL = "mongodb://localhost:27017"

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


# MONGODB SETUP
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DATABASE_URL)
mongodb = client.students
