

from sqlalchemy import Column, Integer, String
from sqlalchemy.types import JSON
from .defs import Base

class RecordEntity(Base):

    __tablename__ = 'coredns_records'

    id = Column(Integer, primary_key=True, nullable=False)
    zone = Column(String, nullable=False)
    name = Column(String, nullable=False)
    ttl = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    record_type = Column(String, nullable=False)



