from sqlalchemy import Column, String, Boolean, inspect

from src.database.constants import NAME_LEN
from src.database.sql import Base, engine


class ChatUserORM(Base):
    """
    User Model
        User ORM
    """
    __tablename__ = 'chat_user'
    uid: str = Column(String(NAME_LEN), primary_key=True, unique=True)
    display_name: str = Column(String(NAME_LEN))
    user_banned: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            Base.metadata.tables[cls.__tablename__].drop(bind=engine)

    def to_dict(self):
        return {
            "uid": self.uid,
            "display_name": self.display_name,
            "user_banned": self.user_banned
        }


class ChatMessageORM(Base):
    __tablename__ = "chat_message"
    uid: str = Column(String(NAME_LEN))
    message_id: str = Column(String(NAME_LEN), primary_key=True)
    text: str = Column(String(NAME_LEN))
    timestamp: str = Column(String(NAME_LEN))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            Base.metadata.tables[cls.__tablename__].drop(bind=engine)

    def to_dict(self):
        return {
            'uid': self.uid,
            'messaged_id': self.message_id,
            'text': self.text,
            'timestamp': self.timestamp
        }
