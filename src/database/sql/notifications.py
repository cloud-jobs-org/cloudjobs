from sqlalchemy import Column, String, Boolean, DateTime, inspect

from src.database.constants import ID_LEN
from src.database.sql import Base, engine


class NotificationORM(Base):
    __tablename__ = 'notifications'
    uid = Column(String(ID_LEN), primary_key=True)
    game_id = Column(String(ID_LEN))
    title = Column(String(ID_LEN))
    message = Column(String(ID_LEN))
    category = Column(String(ID_LEN))
    time_read = Column(DateTime, nullable=True)
    is_read = Column(Boolean)
    time_created = Column(DateTime)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)
