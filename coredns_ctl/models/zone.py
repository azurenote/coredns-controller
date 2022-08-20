
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .defs import Base


class ZoneEntity(Base):
    __tablename__ = 'coredns_zone'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    records = relationship('RecordEntity', lazy='joined')
