from strawberry import type, mutation, input
from strawberry.types import Info
from sqlalchemy import select, update, delete
from coredns_ctl.schema.query import Zone, Record, ObjectId
from coredns_ctl.models import RecordEntity, ZoneEntity


@input
class NewRecord:
    name: str
    zone_id: int
    ttl: int
    record_type: str


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
                query = update(ZoneEntity) \
                    .values(name=name) \
                    .where(ZoneEntity.id == zone_id) \
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
        async with info.context.session() as session:
            async with session.begin():

                query = select(ZoneEntity).where(ZoneEntity.id == data.zone_id)

                result = await session.execute(query)
                zone: ZoneEntity = result.scalar()

                entity = RecordEntity()
                entity.zone_id = data.zone_id
                entity.zone = zone.name
                entity.name = data.name
                entity.ttl = data.ttl
                entity.record_type = data.record_type

                session.add(entity)
                await session.commit()

                return Record(entity)

    @mutation
    async def update_record(self, record_id: int, name: str, info: Info) -> Record:
        async with info.context.session() as session:
            async with session.begin():
                query = update(RecordEntity) \
                    .values(name=name) \
                    .where(RecordEntity.id == record_id) \
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
