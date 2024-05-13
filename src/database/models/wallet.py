import uuid
from datetime import datetime, date

from pydantic import BaseModel, Field, PositiveInt


class TransactionType(str):
    deposit = "deposit"
    payment_from_escrow = "payment_from_escrow"
    withdrawal = "withdrawal"
    transfer_to_escrow = 'transfer_to_escrow'
    transfer_from_escrow = "transfer_from_escrow"


class WalletTransaction(BaseModel):
    """
    Transaction model represents an individual transaction.
    """
    uid: str
    date: datetime = Field(default_factory=datetime.utcnow)
    transaction_type: str
    target_wallet: str | None
    amount: PositiveInt


class WalletConst(BaseModel):
    _max_transaction_amount: PositiveInt = 100_000
    _min_transaction_amount: PositiveInt = 100


class Wallet(WalletConst):
    """
    Wallet class represents a user's wallet with balance and transaction operations.
    """
    uid: str
    balance: int = Field(default=0, description="Balance in Cents")
    escrow: int = Field(default=0, description="Amount in Escrow Account")
    transactions: list[WalletTransaction] = Field(default=[], description="List of transaction details")

    async def transfer_to_escrow(self, amount: PositiveInt) -> WalletTransaction:
        """

        :param amount:
        :return:
        """
        if self.balance == 0:
            raise ValueError("Insufficient Balance to make payment")

        if amount < self._min_transaction_amount:
            raise ValueError(f"Payment amount must be greater than {self._min_transaction_amount}.")

        if amount > self._max_transaction_amount:
            raise ValueError(f"Payment amount must not be more than {self._max_transaction_amount}")

        if amount > self.balance:
            raise ValueError("Insufficient Balance to transfer to Escrow.")
        transaction = await self._record_transaction(amount=amount,
                                                     transaction_type=TransactionType.transfer_to_escrow)
        self.balance -= amount
        self.escrow += amount

        return transaction

    async def pay_from_escrow(self, amount: PositiveInt, target_wallet: str) -> WalletTransaction:
        """
            using balance in escrow pay to a target wallet
        :param target_wallet:
        :param amount:

        :return:
        """
        if self.escrow == 0:
            raise ValueError("Insufficient Balance to make payment")

        if amount < self._min_transaction_amount:
            raise ValueError(f"Payment amount must be greater than {self._min_transaction_amount}.")

        if amount > self._max_transaction_amount:
            raise ValueError(f"Payment amount must not be more than {self._max_transaction_amount}")

        if amount > self.escrow:
            raise ValueError("Insufficient funds in Escrow.")

        # Implement payment processing here
        # You can make API calls to process the payment with a payment gateway

        # For demonstration purposes, we'll just deduct the payment amount from the balance
        transaction = await self._record_transaction(amount=amount,
                                                     transaction_type=TransactionType.payment_from_escrow,
                                                     target_wallet=target_wallet)
        self.escrow -= amount
        return transaction

    async def withdraw_funds(self, amount: PositiveInt) -> WalletTransaction:
        if amount > self.balance:
            raise ValueError("Insufficient funds in the wallet.")
        if amount < self._min_transaction_amount:
            raise ValueError(f"Withdrawal amount must be equal to or greater than {self._min_transaction_amount}")
        if amount > self._max_transaction_amount:
            raise ValueError(f"Withdrawal amount must be less than our Maximum "
                             f"Transaction Amount: {self._max_transaction_amount}")

        # Implement withdrawal processing here
        # You can make API calls to initiate the withdrawal

        # For demonstration purposes, we'll just deduct the withdrawal amount from the balance
        transaction = await self._record_transaction(amount=amount, transaction_type=TransactionType.withdrawal)
        self.balance -= amount
        return transaction

    async def deposit_funds(self, amount: PositiveInt) -> WalletTransaction:
        if amount < self._min_transaction_amount:
            raise ValueError(f"Deposit amount must be equal to or greater than {self._min_transaction_amount}")
        if amount > self._max_transaction_amount:
            raise ValueError(f"Deposit amount must be less than our Maximum "
                             f"Transaction Amount: {self._max_transaction_amount}")

        # Implement deposit processing here
        # You can make API calls to process the deposit with a payment gateway

        # For demonstration purposes, we'll just add the deposit amount to the balance
        transaction = await self._record_transaction(amount=amount, transaction_type=TransactionType.deposit)
        self.balance += amount
        return transaction

    async def get_transactions(self, limit: int | None = None) -> list[WalletTransaction]:
        """
        Get the list of transactions.

        Args:
            limit (Optional[int]): Maximum number of transactions to retrieve. Defaults to None (retrieve all).

        Returns:
            List[Transaction]: List of transaction details.
        """
        if limit is None:
            return self.transactions
        else:
            return self.transactions[-limit:]

    async def get_transaction_count(self) -> int:
        """
        Get the total number of transactions.

        Returns:
            int: Total number of transactions.
        """
        return len(self.transactions)

    async def _record_transaction(self, amount: PositiveInt,
                                  transaction_type: str,
                                  target_wallet: str | None = None) -> WalletTransaction:

        transaction = WalletTransaction(
            uid=self.uid,
            amount=amount,
            transaction_type=transaction_type,
            target_wallet=target_wallet
        )
        self.transactions.append(transaction)
        return transaction


def today():
    return datetime.today()


def create_id():
    return str(uuid.uuid4())


class WithdrawalRequests(BaseModel):
    uid: str
    request_id: str = Field(default_factory=create_id)
    withdrawal_amount: int
    date_created: date = Field(default_factory=today)
    is_valid: bool = Field(default=False)
    is_processed: bool = Field(default=False)
