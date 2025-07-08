__all__ = ('TransactionsPage', )

from dataclasses import dataclass
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.finances import TransactionPreviewsBatch


@dataclass
class TransactionsPage(FunPayPage):
    """
    Represents the transactions page (https://funpay.com/account/balance).
    """

    rub_balance: MoneyValue | None
    """RUB balance."""

    usd_balance: MoneyValue | None
    """USD balance."""

    eur_balance: MoneyValue | None
    """EUR balance."""

    transactions: TransactionPreviewsBatch | None
    """Transaction previews."""
