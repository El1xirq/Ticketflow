from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends

from typing import Annotated

from app.core.config import settings

engine = create_async_engine(settings.db_url)
session_local = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with session_local() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]

class Base(DeclarativeBase):
    pass
