from sqlalchemy import Column, ForeignKey, Integer, BIGINT, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from ssm import Base


class BlogsServer(Base):
	__tablename__ = 'blogs_server'

	id = Column(Integer, primary_key=True, autoincrement=True)
	server_id = Column(BIGINT, unique=True)
	blogs_category = relationship("BlogsCategory", backref='blogs_server', lazy='dynamic')


class BlogsCategory(Base):
	__tablename__ = 'blogs_category'
	__table_args__ = (UniqueConstraint('category_id'),)

	id = Column(BIGINT, primary_key=True, autoincrement=True)
	server_id = Column(BIGINT, ForeignKey('blogs_server.server_id', onupdate='CASCADE', ondelete='CASCADE'))
	category_id = Column(BIGINT)
	blogs_channel = relationship("BlogsChannel", backref='blogs_category', lazy='dynamic')


class BlogsChannel(Base):
	__tablename__ = 'blogs_channel'
	id = Column(Integer, primary_key=True, autoincrement=True)
	category_id = Column(BIGINT, ForeignKey('blogs_category.category_id', onupdate='CASCADE', ondelete='CASCADE'))
	channel_id = Column(BIGINT, unique=True)
	owner_id = Column(BIGINT)
	sub_user_list = Column(JSON)
