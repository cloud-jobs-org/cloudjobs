from datetime import datetime, date

from sqlalchemy import Column, Integer, String, DateTime, inspect, Text, Date, Boolean

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import engine, Base


class WalletTransactionORM(Base):
    __tablename__ = 'wallet_transactions'
    transaction_id: str = Column(String(ID_LEN), primary_key=True)
    uid: str = Column(String(ID_LEN), nullable=False)
    date: datetime = Column(DateTime)
    transaction_type: str = Column(String(16), nullable=False)
    pay_to_wallet: str = Column(String(ID_LEN), nullable=False)
    payment_from_wallet: str = Column(String(ID_LEN), nullable=False)
    amount: int = Column(Integer, nullable=False)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self) -> dict:
        """
        Convert the WalletTransaction object to a dictionary representation.

        Returns:
            dict: Dictionary containing the attributes of the WalletTransaction.
        """
        return {
            "transaction_id": self.transaction_id,
            "uid": self.uid,
            "date": self.date,
            "transaction_type": self.transaction_type,
            "pay_to_wallet": self.pay_to_wallet,
            "payment_from_wallet": self.payment_from_wallet,
            "amount": self.amount,
        }

    def __eq__(self, other):
        """
        Override the equality dunder method to compare WalletTransaction instances based on transaction_id and uid.

        Args:
            other (WalletTransaction): The other instance to compare with.

        Returns:
            bool: True if the two instances have the same transaction_id and uid, False otherwise.
        """
        if not isinstance(other, WalletTransactionORM):
            return False
        return (self.transaction_id == other.transaction_id) and (self.uid == other.uid)


class WalletORM(Base):
    __tablename__ = "wallet"
    uid: str = Column(String(ID_LEN), primary_key=True)
    balance: int = Column(Integer)
    escrow: int = Column(Integer)
    transactions: str = Column(Text)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self) -> dict[str, str | int | list[str]]:
        return {
            'uid': self.uid,
            'balance': self.balance,
            'escrow': self.escrow,
            'transactions': self.transactions.split(",")
        }


class WithdrawalRequestsORM(Base):
    __tablename__ = "withdrawal_requests"
    uid: str = Column(String(ID_LEN))
    request_id: str = Column(String(ID_LEN), primary_key=True)
    withdrawal_amount: int = Column(Integer)
    date_created: date = Column(Date)
    is_valid: bool = Column(Boolean)
    is_processed: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self) -> dict[str, str | int | list[str]]:
        return {
            'uid': self.uid,
            'request_id': self.request_id,
            'withdrawal_amount': self.withdrawal_amount,
            'date_created': self.date_created,
            'is_valid': self.is_valid
        }
