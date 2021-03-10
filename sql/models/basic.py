from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table
from sqlalchemy.orm import relationship

from settings import Base, engine


class Reactions(Base):
    __tablename__ = 'reactions'
    id = Column(Integer, autoincrement=True, primary_key=True)
    message_id = Column(BIGINT, primary_key=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'message_id': self.message_id,
        }
