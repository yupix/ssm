from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from settings import Base, engine


class NotesUser(Base):
    __tablename__ = 'notes_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
        }


class NotesCategory(Base):
    __tablename__ = 'notes_category'
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_name = Column(VARCHAR(255), unique=True)


class NotesDetail(Base):
    __tablename__ = 'notes_detail'
    __table_args__ = (UniqueConstraint('user_id', 'content', 'category_name'),)

    id = Column(BIGINT, primary_key=True, autoincrement=True)  # TODO: 2021/01/15/ 複合キーになっているため、ここを修正しないとカテゴリとコンテンツによる複合がきちんと機能しない
    user_id = Column(BIGINT, ForeignKey('notes_user.user_id', onupdate='CASCADE', ondelete='CASCADE'))
    content = Column(VARCHAR(255))
    category_name = Column(VARCHAR(255))

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
