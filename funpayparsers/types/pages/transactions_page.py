__all__ = ('TransactionsPage', )

from dataclasses import dataclass
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.finances import TransactionPreviewsBatch


@dataclass
class TransactionsPage(FunPayPage):
    """
    Represents a FunPay transactions page.
    """

    rub_balance: MoneyValue
    """RUB balance."""

    usd_balance: MoneyValue
    """USD balance."""

    eur_balance: MoneyValue
    """EUR balance."""

    transactions: TransactionPreviewsBatch | None
    """Transaction previews."""
