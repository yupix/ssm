from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table
from sqlalchemy.orm import relationship

from settings import Base, engine


class NotesUser(Base):
    __tablename__ = 'notes_user'

    id = Column(Integer, autoincrement=True)
    user_id = Column(BIGINT, primary_key=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
        }


class NotesCategory(Base):
    __tablename__ = 'notes_category'

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    category_name = Column(VARCHAR(255))


class NotesDetail(Base):
    __tablename__ = 'notes_detail'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey('notes_user.user_id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    content = Column(VARCHAR(255), nullable=False, primary_key=True)
    category_name = Column(VARCHAR(255), primary_key=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'category_name': self.category_name,
        }


Base.metadata.create_all(engine)
