from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


from config import settings_db

DATABASE_URL = f"postgresql+asyncpg://{settings_db.DB_USER}:{settings_db.DB_PASS}@{settings_db.DB_HOST}:{settings_db.DB_PORT}/{settings_db.DB_NAME}"

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass