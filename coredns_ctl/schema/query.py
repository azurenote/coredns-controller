from strawberry import type, field, union, mutation, input
from strawberry.types import Info
from datetime import datetime
from base64 import b64encode
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
    created_at: datetime

    def __init__(self, entity: RecordEntity):
        self.id = entity.id
        self.name = entity.name
        self.zone = entity.zone
        self.ttl = entity.ttl
        self.record_type = entity.record_type
        self.zone_id = entity.zone_id
        self.created_at = entity.created_at

        match entity.record_type:
            case 'A':
                self.content = RecordA(**entity.content)
            case 'MX':
                self.content = RecordMX(**entity.content)


@type
class PageInfo:
    hasNextPage: bool


@type
class ZoneRecordsEdge:
    """ Edge type """
    cursor: str
    node: Record

    def __init__(self, node: Record, cursor: str = None):
        self.node = node
        self.cursor = cursor if cursor is not None\
            else b64encode(node.id.to_bytes(byteorder='little', length=4))


@type
class ZoneRecordsConnection:
    """
    Connection type.
    :see: https://www.apollographql.com/blog/graphql/explaining-graphql-connections
    """
    page_info: PageInfo
    edges: list[ZoneRecordsEdge]

    def __init__(self, page_info: PageInfo, edges: list[ZoneRecordsEdge]):
        self.page_info = page_info
        self.edges = edges


@type
class Zone:
    id: int
    name: str
    created_at: datetime

    def __init__(self, entity: ZoneEntity):
        self.id = entity.id
        self.name = entity.name
        self.created_at = entity.created_at
        self.records = entity.records

    @field
    async def records_connection(self, info: Info, offset: int = 0, size: int = 10) -> ZoneRecordsConnection:

        async with info.context.session() as session:
            async with session.begin():

                query = select(RecordEntity)\
                    .where(RecordEntity.zone_id == self.id) \
                    .offset(offset)\
                    .limit(size)

                result = await session.execute(query)
                items = result.scalars()

                page_info = PageInfo(True)
                edges = [
                    ZoneRecordsEdge(node=Record(item))
                    for item in items
                ]

                return ZoneRecordsConnection(page_info, edges)


@type
class ObjectId:
    id: int

    def __init__(self, object_id: int):
        self.id = object_id


@type
class Query:
    @field
    async def records(self, info: Info, zone_id: int = 0) -> list[Record]:
        async with info.context.session() as session:
            async with session.begin():
                query = select(RecordEntity)

                if zone_id > 0:
                    query = query.where(RecordEntity.zone_id == zone_id)

                result = await session.execute(query)

                return [
                    Record(record)
                    for record in result.scalars()
                ]

    @field
    async def record(self, record_id: int, info: Info) -> Record:
        async with info.context.session() as session:
            async with session.begin():
                query = select(RecordEntity).where(RecordEntity.id == record_id).limit(1)
                result = await session.execute(query)

                return Record(result.scalar())

    @field
    async def zone(self, zone_id: int, info: Info) -> Zone:
        async with info.context.session() as session:
            async with session.begin():
                query = select(ZoneEntity).where(ZoneEntity.id == zone_id).limit(1)
                result = await session.execute(query)

                return Zone(result.scalar())

    @field
    async def zones(self, info: Info, offset: int = 0, size: int = 10) -> list[Zone]:
        output = []

        async_session = info.context.session

        async with async_session() as session:
            async with session.begin():
                stmt = select(ZoneEntity)\
                    .order_by(ZoneEntity.id.desc())\
                    .offset(offset)\
                    .limit(size)

                result = await session.execute(stmt)

                temp = result.scalars()

                for record in temp:
                    item = Zone(record)

                    output.append(item)

        return output
