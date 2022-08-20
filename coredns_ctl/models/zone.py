
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from .defs import Base


class ZoneEntity(Base):
    __tablename__ = 'coredns_zone'
    __mapper_args__ = {'eager_defaults': True}

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=now())

    records = relationship('RecordEntity', lazy=None)
