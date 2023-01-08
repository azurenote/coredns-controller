import logging

from strawberry import type, mutation, input
from strawberry.types import Info
from sqlalchemy import select, update, delete
from coredns_ctl.schema.query import Zone, Record, ObjectId
from coredns_ctl.models import RecordEntity, ZoneEntity
import json


@input
class NewRecord:
    name: str
    zone_id: int
    ttl: int


@input
class NewARecord:
    common: NewRecord
    ip: str


@input
class NewMxRecord:
    common: NewRecord
    host: str
    priority: int


@input
class NewCnameRecord:
    common: NewRecord
    host: str


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
    async def add_a_record(self, data: NewARecord, info: Info) -> Record:
        async with info.context.session() as session:
            async with session.begin():
                try:
                    query = select(ZoneEntity).where(ZoneEntity.id == data.common.zone_id)

                    result = await session.execute(query)
                    zone: ZoneEntity = result.scalar()

                    entity = RecordEntity()
                    entity.zone_id = data.common.zone_id
                    entity.zone = zone.name
                    entity.name = data.common.name
                    entity.ttl = data.common.ttl
                    entity.record_type = 'A'
                    entity.content = {
                        'ip': data.ip
                    }

                    session.add(entity)
                    await session.flush()

                    query = select(RecordEntity).where(RecordEntity.id == entity.id)
                    result = await session.execute(query)

                    record = result.scalar()

                    record.content = json.loads(record.content)
                    return Record(record)
                except Exception as ex:
                    logging.error(ex)
                    await session.rollback()

    @mutation
    async def add_mx_record(self, data: NewMxRecord, info: Info) -> Record:
        async with info.context.session() as session:
            async with session.begin():
                try:
                    query = select(ZoneEntity).where(ZoneEntity.id == data.common.zone_id)

                    result = await session.execute(query)
                    zone: ZoneEntity = result.scalar()

                    entity = RecordEntity()
                    entity.zone_id = data.common.zone_id
                    entity.zone = zone.name
                    entity.name = data.common.name
                    entity.ttl = data.common.ttl
                    entity.record_type = 'MX'
                    entity.content = json.dumps({
                        'host': data.host,
                        'priority': data.priority
                    })

                    session.add(entity)
                    await session.flush()

                    query = select(RecordEntity).where(RecordEntity.id == entity.id)
                    result = await session.execute(query)

                    record = result.scalar()

                    record.content = json.loads(record.content)
                    return Record(record)
                except Exception as ex:
                    logging.error(ex)
                    await session.rollback()

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
