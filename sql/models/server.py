from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from settings import Base, engine


class NotesUser(Base):
    __tablename__ = 'notes_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(BIGINT, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'server_id': self.server_id,
        }

Base.metadata.create_all(engine)
