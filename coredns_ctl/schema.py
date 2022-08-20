from sqlalchemy.orm import joinedload
from strawberry import type, field, union, Schema, mutation, input
from strawberry.types import Info
from datetime import datetime

from sqlalchemy import select, update, delete
from coredns_ctl.models import RecordEntity, ZoneEntity


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
    zone_id: int

    def __init__(self, entity: RecordEntity):
        self.id = entity.id
        self.name = entity.name
        self.zone = entity.zone
        self.ttl = entity.ttl
        self.record_type = entity.record_type
        self.zone_id = entity.zone_id

        match entity.record_type:
            case 'A':
                self.content = RecordA(**entity.content)
            case 'MX':
                self.content = RecordMX(**entity.content)


@input
class NewRecord:
    name: str
    zone_id: int
    ttl: int
    record_type: str


@type
class Zone:
    id: int
    name: str
    create_at: datetime

    records: list[Record]

    def __init__(self, entity: ZoneEntity):
        self.id = entity.id
        self.name = entity.name
        self.create_at = entity.created_at
        self.records = entity.records


@type
class ObjectId:
    id: int

    def __init__(self, object_id: int):
        self.id = object_id


@type
class Query:
    @field
    async def records(self, info: Info) -> list[Record]:
        output = []

        async_session = info.context.session

        async with async_session() as session:
            async with session.begin():
                stmt = select(RecordEntity)

                result = await session.execute(stmt)

                temp = result.scalars()

                for record in temp:
                    item = Record(record)

                    output.append(item)

        return output

    @field
    async def zones(self, info: Info) -> list[Zone]:
        output = []

        async_session = info.context.session

        async with async_session() as session:
            async with session.begin():
                stmt = select(ZoneEntity)\
                    .options(joinedload(ZoneEntity.records))

                result = await session.execute(stmt)

                temp = result.scalars()

                for record in temp:
                    item = Zone(record)

                    output.append(item)

        return output


@type
class Mutation:

    @mutation
    async def add_zone(self, name: str, info: Info) -> Zone:
        async_session = info.context.session

        async with async_session() as session:
            async with session.begin():
                entity = ZoneEntity()
                entity.name = name

                session.add(entity)
                await session.commit()

                return Zone(entity)

    @mutation
    async def update_zone(self, zone_id: int, name: str, info: Info) -> Zone:
        async with info.context.session() as session:
            async with session.begin():
                query = update(ZoneEntity)\
                    .values(name=name)\
                    .where(ZoneEntity.id == zone_id)\
                    .execution_options(synchronize_session='fetch')

                await session.execute(query)

                q_select = select(ZoneEntity).where(ZoneEntity.id == zone_id)

                result = await session.execute(q_select)
                return Zone(result.scalar())

    @mutation
    async def delete_zone(self, zone_id: int, info: Info) -> ObjectId:
        async with info.context.session() as session:
            async with session.begin():
                query = delete(ZoneEntity).where(ZoneEntity.id == zone_id)

                await session.execute(query)

                return ObjectId(zone_id)

    @mutation
    async def add_record(self, data: NewRecord, info: Info) -> Record:
        async_session = info.context.session

        async with async_session() as session:
            async with session.begin():
                entity = RecordEntity()
                entity.zone_id = data.zone_id
                entity.name = data.name
                entity.ttl = data.ttl

                session.add(entity)
                await session.commit()

        return Record(entity)

    @mutation
    async def update_record(self, record_id: int, name: str, info: Info) -> Record:
        async with info.context.session() as session:
            async with session.begin():
                query = update(RecordEntity)\
                    .values(name=name)\
                    .where(RecordEntity.id == record_id)\
                    .execution_options(synchronize_session='fetch')

                await session.execute(query)

                q_select = select(RecordEntity).where(RecordEntity.id == record_id)

                result = await session.execute(q_select)
                return Record(result.scalar())

    @mutation
    async def delete_record(self, record_id: int, info: Info) -> ObjectId:
        async with info.context.session() as session:
            async with session.begin():
                query = delete(RecordEntity).where(RecordEntity.id == record_id)

                await session.execute(query)

                return ObjectId(record_id)


schema = Schema(query=Query, mutation=Mutation)
