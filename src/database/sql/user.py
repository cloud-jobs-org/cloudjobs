from sqlalchemy import Column, String, Boolean, ForeignKey, inspect, Integer

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class UserORM(Base):
    """
    User Model
        User ORM
    """
    __tablename__ = 'users'
    uid: str = Column(String(ID_LEN), primary_key=True, unique=True)
    customer_id: str = Column(String(ID_LEN), nullable=True)
    username: str = Column(String(NAME_LEN))
    password_hash: str = Column(String(255))
    email: str = Column(String(256))
    account_verified: bool = Column(Boolean, default=False)
    is_system_admin: bool = Column(Boolean, default=False)

    is_company_admin: bool = Column(Boolean, default=False)
    is_employee: bool = Column(Boolean, default=False)
    is_client: bool = Column(Boolean, default=False)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def __init__(self,
                 uid: str,
                 username: str,
                 password_hash: str,
                 email: str,
                 customer_id: str = None,

                 account_verified: bool = False,
                 is_system_admin: bool = False,
                 is_company_admin: bool = False,
                 is_employee: bool = False,
                 is_client: bool = False
                 ):
        self.uid = uid
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.account_verified = account_verified
        self.customer_id = customer_id

        self.is_system_admin = is_system_admin
        self.is_company_admin = is_company_admin
        self.is_employee = is_employee
        self.is_client = is_client

    def __bool__(self) -> bool:
        return bool(self.uid) and bool(self.username) and bool(self.email)

    def to_dict(self) -> dict[str, str | bool]:
        return {
            'uid': self.uid,
            'customer_id': self.customer_id,

            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'account_verified': self.account_verified,
            'is_system_admin': self.is_system_admin,
            'is_company_admin': self.is_company_admin,
            'is_employee': self.is_employee,
            'is_client': self.is_client
        }


class PayPalORM(Base):
    __tablename__ = 'paypal_account'
    uid = Column(String(NAME_LEN), primary_key=True)
    paypal_email: str = Column(String(NAME_LEN))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self) -> dict[str, str]:
        return {
            'uid': self.uid,
            'paypal_email': self.paypal_email
        }
