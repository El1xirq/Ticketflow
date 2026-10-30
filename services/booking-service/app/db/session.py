from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase

from typing import Annotated

from app.config import settings

engine = create_async_engine(settings.db_url)
session_local = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with session_local() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]

class Base(DeclarativeBase):
    pass