from os import environ
from dotenv import load_dotenv
from strawberry import type, field, union, Schema
from datetime import datetime


from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy import select
from coredns_ctl.models import RecordEntity, ZoneEntity


@type
class Zone:
    id: int
    name: str
    create_at: datetime

    def __init__(self, entity: ZoneEntity):
        self.id = entity.id
        self.name = entity.name
        self.create_at = entity.created_at

@type
class RecordA:
    ip: str


@type
class RecordMX:
    host: str
    priority: int


@type
class Record:
    id: int
    name: str
    zone: str
    ttl: int
    content: union('RecordContent', types=(RecordA, RecordMX))
    record_type: str

    def __init__(self, entity: RecordEntity):
        self.id = entity.id
        self.name = entity.name
        self.zone = entity.zone
        self.ttl = entity.ttl
        self.record_type = entity.record_type

        match entity.record_type:
            case 'A':
                self.content = RecordA(**entity.content)
            case 'MX':
                self.content = RecordMX(**entity.content)


@type
class Query:
    @field
    async def records(self) -> list[Record]:

        load_dotenv()

        engine = create_async_engine(
            environ.get('DATABASE_URL'),
            echo=True,
        )

        output = []

        async with engine.begin() as conn:
            # select a Result, which will be delivered with buffered
            # results
            async_session = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )

            async with async_session() as session:

                async with session.begin():
                    stmt = select(RecordEntity)

                    result = await session.execute(stmt)

                    temp = result.scalars()

                    for record in temp:
                        item = Record(record)

                        output.append(item)
            
        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()

        return output

    @field
    async def zones(self) -> list[Zone]:
        load_dotenv()

        engine = create_async_engine(
            environ.get('DATABASE_URL'),
            echo=True,
        )

        output = []

        async with engine.begin() as conn:
            # select a Result, which will be delivered with buffered
            # results
            async_session = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )

            async with async_session() as session:
                async with session.begin():
                    stmt = select(ZoneEntity)

                    result = await session.execute(stmt)

                    temp = result.scalars()

                    for record in temp:
                        item = Zone(record)

                        output.append(item)

        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()

        return output



schema = Schema(query=Query)
