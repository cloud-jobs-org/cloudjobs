from sqlalchemy import Column, String, inspect

from src.database.constants import ID_LEN
from src.database.sql import Base, engine


class AddressORM(Base):
    __tablename__ = "addresses"
    address_id = Column(String(ID_LEN), primary_key=True)
    address_line_1 = Column(String(255))
    town_city = Column(String(100))
    province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))

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
            "address_id": self.address_id,
            "address_line_1": self.address_line_1,
            "town_city": self.town_city,
            "province": self.province,
            "country": self.country,
            "postal_code": self.postal_code
        }


class ContactsORM(Base):
    __tablename__ = "contacts"
    contact_id = Column(String(ID_LEN), primary_key=True)
    cell = Column(String(20))
    tel = Column(String(20), nullable=True)
    email = Column(String(255))
    facebook = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    whatsapp = Column(String(20), nullable=True)

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
            "contact_id": self.contact_id,
            "cell": self.cell,
            "tel": self.tel,
            "email": self.email,
            "facebook": self.facebook,
            "twitter": self.twitter,
            "whatsapp": self.whatsapp
        }


class PostalAddressORM(Base):
    __tablename__ = "postal_addresses"
    postal_id = Column(String(ID_LEN), primary_key=True)
    address_line_1 = Column(String(255))
    town_city = Column(String(100))
    province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))

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
            "postal_id": self.postal_id,
            "address_line_1": self.address_line_1,
            "town_city": self.town_city,
            "province": self.province,
            "country": self.country,
            "postal_code": self.postal_code
        }
