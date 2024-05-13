from sqlalchemy import Column, String, inspect, Boolean

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class CustomerDetailsORM(Base):
    __tablename__ = "customer_details"
    customer_id = Column(String(ID_LEN), primary_key=True)
    uid = Column(String(ID_LEN))

    full_names = Column(String(NAME_LEN))
    surname = Column(String(NAME_LEN))

    email = Column(String(255))
    contact_number = Column(String(18))

    date_joined = Column(String(36))

    is_active = Column(Boolean)

    delivery_address_id = Column(String(ID_LEN))
    address_id = Column(String(ID_LEN))
    contact_id = Column(String(ID_LEN))
    postal_id = Column(String(ID_LEN))
    bank_account_id = Column(String(ID_LEN))

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
            'customer_id': self.customer_id,
            'uid': self.uid,
            'full_names': self.full_names,
            'surname': self.surname,
            'email': self.email,
            'contact_number': self.contact_number,
            'delivery_address_id': self.delivery_address_id,

            'date_joined': self.date_joined,
            'is_active': self.is_active,
            'address_id': self.address_id,
            'contact_id': self.contact_id,
            'postal_id': self.postal_id,
            'bank_account_id': self.bank_account_id
        }
