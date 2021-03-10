from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from settings import Base, engine


class ApiRequests(Base):
    __tablename__ = 'api_requests'
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    request_id = Column(Integer, unique=True)
    type = Column(VARCHAR(255))


class ApiDetail(Base):
    __tablename__ = 'api_detail'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    request_id = Column(BIGINT, ForeignKey('api_requests.request_id', onupdate='CASCADE', ondelete='CASCADE'), unique=True)
    content = Column(JSON)
