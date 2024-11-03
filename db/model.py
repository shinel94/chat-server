from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class RoomType(enum.IntEnum):
    PRIVATE = 100
    GROUP = 200

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    chatrooms = relationship('UserChatroom', back_populates='user')
    created_at = Column(DateTime, default=datetime.now)

class Chatroom(Base):

    __tablename__ = 'chatrooms'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship('UserChatroom', back_populates='chatroom')
    room_type = Column(Enum(RoomType), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now)


class UserChatroom(Base):
    __tablename__ = 'user_chatrooms'


    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    chatroom_id = Column(Integer, ForeignKey('chatrooms.id'))

    user = relationship('User', back_populates='chatrooms')
    chatroom = relationship('Chatroom', back_populates='users')

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now)

class UserChatLog(Base):
    __tablename__ = 'user_chat_log'


    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chatroom_id = Column(Integer, ForeignKey('chatrooms.id'))
    message = Column(String,)
    created_at = Column(DateTime, default=datetime.now)

if __name__ == "__main__":
    from db.engine import engine
    Base.metadata.create_all(engine)