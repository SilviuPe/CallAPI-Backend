from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ClientSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_hash = Column(String)
    expires_at = Column(DateTime)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Endpoint(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id"))
    url = Column(String)
    method = Column(String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}