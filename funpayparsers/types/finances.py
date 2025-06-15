__all__ = ('TransactionPreview',)


from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.enums import PaymentMethod, TransactionStatus


@dataclass
class TransactionPreview(FunPayObject):
    """
    Represents a transaction preview.
    """

    id: int
    """Unique transaction ID."""

    date_text: str
    """Transaction date (as human-readable text)."""

    desc: str
    """Transaction description."""

    status: TransactionStatus
    """Transaction status."""

    amount: MoneyValue
    """Transaction amount."""

    payment_method: PaymentMethod | None
    """Payment method, if applicable."""

    withdrawal_number: str | None
    """Withdrawal card / phone / wallet number, if applicable."""


@dataclass
class Transaction(FunPayObject): ...  # todo


@dataclass
class WithdrawalTransaction(Transaction): ...


@dataclass
class DepositTransaction(Transaction): ...


@dataclass
class OrderTransaction(Transaction): ...
