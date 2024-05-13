from flask import Flask
from pydantic import PositiveInt

from src.controller import Controllers, error_handler
from src.database.models.users import User
from src.database.models.wallet import Wallet, WalletTransaction, TransactionType, WithdrawalRequests
from src.database.sql.wallet import WalletTransactionORM, WithdrawalRequestsORM


class WalletController(Controllers):
    def __init__(self):
        super().__init__()
        self.wallets: dict[str, Wallet] = {}


    def load_and_build_wallets(self):
        wallets_by_uid = {}
        with self.get_session() as session:
            transactions_orm_list = session.query(WalletTransactionORM).filter().all()
            transactions_list = [WalletTransaction(**transaction_orm.to_dict())
                                 for transaction_orm in transactions_orm_list]

            for transaction in transactions_list:
                # Check if the wallet already exists in the dictionary, otherwise create a new one
                if transaction.uid not in self.wallets:
                    self.wallets[transaction.uid] = Wallet(
                        uid=transaction.uid,
                        transactions=[],
                    )
                # Add the transaction to the user's wallet

                self.wallets[transaction.uid].transactions.append(transaction)

                # Calculate the balance based on the transaction type
                if transaction.transaction_type == TransactionType.deposit:
                    self.wallets[transaction.uid].balance += transaction.amount

                elif transaction.transaction_type == TransactionType.withdrawal:
                    """withdrawing from balance to your paypal account"""
                    self.wallets[transaction.uid].balance -= transaction.amount

                elif transaction.transaction_type == TransactionType.payment_from_escrow:
                    """payment from escrow to another account balance"""
                    self.wallets[transaction.uid].escrow -= transaction.amount
                    self.wallets[transaction.target_wallet].balance -= transaction.amount

                elif transaction.transaction_type == TransactionType.transfer_to_escrow:
                    self.wallets[transaction.uid].balance -= transaction.amount
                    self.wallets[transaction.uid].escrow += transaction.amount

                elif transaction.transaction_type == TransactionType.transfer_from_escrow:
                    self.wallets[transaction.uid].balance += transaction.amount
                    self.wallets[transaction.uid].escrow -= transaction.amount

    def init_app(self, app: Flask):
        """

        :param app:
        :return:
        """
        self.load_and_build_wallets()

    async def get_wallet(self, uid: str) -> Wallet:
        """
            will return data contained in a certain wallet
        :param uid:
        :return:
        """
        if uid not in self.wallets.keys():
            self.wallets[uid] = Wallet(uid=uid)

        return self.wallets[uid]

    async def update_wallets(self):
        """
            this will force an update for wallet transactions
        :return:
        """
        self.load_and_build_wallets()
        return True

    @error_handler
    async def add_transaction(self, transaction: WalletTransaction) -> bool:
        """

        :param transaction:
        :return:
        """
        with self.get_session() as session:
            transaction_orm = WalletTransactionORM(**transaction.dict())
            session.add(transaction_orm)
            session.commit()
            return True

    @error_handler
    async def create_withdrawal_request(self, user: User, withdrawal: WithdrawalRequests):
        with self.get_session() as session:
            withdrawal_orm = WithdrawalRequestsORM(**withdrawal.dict())
            session.add(withdrawal_orm)
            session.commit()
            return withdrawal



