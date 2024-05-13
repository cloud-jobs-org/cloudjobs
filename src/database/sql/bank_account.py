from sqlalchemy import Column, String, inspect

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class BankAccountORM(Base):
    __tablename__ = 'bank_accounts'
    bank_account_id = Column(String(ID_LEN))
    account_holder = Column(String(NAME_LEN))
    account_number = Column(String(NAME_LEN), primary_key=True)
    bank_name = Column(String(NAME_LEN), index=True)
    branch = Column(String(NAME_LEN))
    account_type = Column(String(NAME_LEN))

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
            'bank_account_id': self.bank_account_id,
            'account_holder': self.account_holder,
            'account_number': self.account_number,
            'bank_name': self.bank_name,
            'branch': self.branch,
            'account_type': self.account_type
        }