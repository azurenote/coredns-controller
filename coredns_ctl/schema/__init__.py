from strawberry import Schema
from .query import Record, RecordA, RecordMX, Query
from .mutation import Mutation


schema = Schema(query=Query, mutation=Mutation)

__all__ = (
    schema,
    Query,
    Mutation
)
