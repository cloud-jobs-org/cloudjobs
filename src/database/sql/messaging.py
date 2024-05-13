from sqlalchemy import Column, String, inspect, Integer, Boolean, Text

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class SMSInboxORM(Base):
    __tablename__ = "sms_inbox"

    message_id: str = Column(String(ID_LEN), primary_key=True)
    to_branch: str = Column(String(ID_LEN))
    parent_reference: str = Column(String(ID_LEN), nullable=True)
    from_cell: str = Column(String(17))
    is_response: bool = Column(Boolean)
    previous_history: str = Column(Text)
    message: str = Column(Text)
    date_time_received: str = Column(String(36))
    is_read: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            "from_cell": self.from_cell,

            "to_branch": self.to_branch,
            "message_id": self.message_id,
            "is_response": self.is_response,
            "parent_reference": self.parent_reference,
            "message": self.message,
            "date_time_received": self.date_time_received,
            "is_read": self.is_read
        }


class SMSComposeORM(Base):
    __tablename__ = "sms_compose"

    message_id: str = Column(String(ID_LEN), primary_key=True)
    reference: str = Column(String(ID_LEN))
    message: str = Column(Text)
    from_cell: str = Column(String(17))
    to_cell: str = Column(String(17))
    to_branch: str = Column(String(ID_LEN))
    recipient_type: str = Column(String(36))
    date_time_composed: str = Column(String(36))
    date_time_sent: str = Column(String(36))
    is_delivered: bool = Column(Boolean)
    client_responded: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            "message_id": self.message_id,
            "message": self.message,
            "reference": self.reference,
            "from_cell": self.from_cell,
            "to_cell": self.to_cell,
            "to_branch": self.to_branch,
            "recipient_type": self.recipient_type,
            "date_time_composed": self.date_time_composed,
            "date_time_sent": self.date_time_sent,
            "is_delivered": self.is_delivered,
            "client_responded": self.client_responded
        }


class ContactFormORM(Base):
    __tablename__ = "contact_form"
    uid: str = Column(String(ID_LEN))
    contact_id: str = Column(String(ID_LEN), primary_key=True)
    original_contact_id: str = Column(String(ID_LEN))
    name: str = Column(String(NAME_LEN))
    email: str = Column(String(255))
    message: str = Column(Text)
    datetime_submitted: str = Column(String(36))
    issue_resolved: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            "uid": self.uid,
            "contact_id": self.contact_id,
            "original_contact_id": self.original_contact_id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "datetime_submitted": self.datetime_submitted,
            "issue_resolved": self.issue_resolved
        }