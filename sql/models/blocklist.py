from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table
from sqlalchemy.orm import relationship

from settings import Base, engine


class BlocklistServer(Base):
    __tablename__ = 'blocklist_server'
    server_id = Column(BIGINT, primary_key=True)
    blocklist_settings = relationship("BlocklistSettings", backref='blocklist_settings', lazy='dynamic', cascade="all, delete-orphan")


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'server_id': self.server_id,
        }


class BlocklistSettings(Base):
    __tablename__ = 'blocklist_settings'
    server_id = Column(BIGINT, ForeignKey('blocklist_server.server_id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    mode = Column(VARCHAR(255))
    role = Column(VARCHAR(255))


class BlocklistUser(Base):
    __tablename__ = 'blocklist_user'
    server_id = Column(BIGINT, ForeignKey('blocklist_server.server_id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    user_id = Column(BIGINT, primary_key=True)
    mode = Column(VARCHAR(255))


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'server_id': self.server_id,
            'user_id': self.user_id,
            'mode': self.mode,
        }
