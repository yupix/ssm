from sqlalchemy import Column, VARCHAR, BIGINT, JSON

from ssm import Base


class ApiRequests(Base):
    __tablename__ = 'api_requests'
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    request_id = Column(BIGINT, unique=True)
    request_content = Column(JSON)
    type = Column(VARCHAR(255))


class ApiDetail(Base):
    __tablename__ = 'api_detail'
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    request_id = Column(BIGINT, unique=True)
    content = Column(JSON)
