from os import environ
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi import Depends


async def create_engine():
    engine = create_async_engine(
        environ.get('DATABASE_URL'),
        echo=True,
        pool_size=20,
        max_overflow=0,
        pool_use_lifo=True,
        pool_pre_ping=True
    )

    try:
        async with engine.begin() as conn:
            yield engine, conn
    finally:
        await engine.dispose()


def get_session(engine_connection=Depends(create_engine)):
    try:
        engine, connection = engine_connection
        yield sessionmaker(
            engine, class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    finally:
        pass
