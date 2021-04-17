from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from ssm import Base


class BlogsServer(Base):
    __tablename__ = 'blogs_server'

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(BIGINT, unique=True)
    blogs_category = relationship("BlogsCategory", backref='blogs_server', lazy='dynamic')

class BlogsCategory(Base):
    __tablename__ = 'blogs_category'
    __table_args__ = (UniqueConstraint('server_id', 'category_id'),)

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    server_id = Column(BIGINT, ForeignKey('blogs_server.server_id', onupdate='CASCADE', ondelete='CASCADE'))
    category_id = Column(BIGINT)
