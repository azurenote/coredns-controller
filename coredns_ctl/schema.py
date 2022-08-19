from strawberry import type, field, union, Schema, mutation
from strawberry.types import Info
from datetime import datetime

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
                stmt = select(ZoneEntity)

                result = await session.execute(stmt)

                temp = result.scalars()

                for record in temp:
                    item = Zone(record)

                    output.append(item)

        return output


class Mutation:

    @mutation
    async def add_zone(self, name: str) -> Zone:
        entity = ZoneEntity()
        entity.name = name

        return Zone(entity)

    async def update_zone(self) -> Zone:
        pass

    async def delete_zone(self):
        pass

    @mutation
    async def add_record(self) -> Record:
        pass

    async def update_record(self) -> Record:
        pass

    async def delete_record(self):
        pass


schema = Schema(query=Query)
