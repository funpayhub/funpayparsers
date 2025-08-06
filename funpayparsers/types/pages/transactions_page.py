from __future__ import annotations


__all__ = ('TransactionsPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.common import MoneyValue
from funpayparsers.types.finances import TransactionPreviewsBatch
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.transactions_page_parser import (
        TransactionsPageParsingOptions,
    )


@dataclass
class TransactionsPage(FunPayPage):
    """Represents the transactions page (https://funpay.com/account/balance)."""

    rub_balance: MoneyValue | None
    """RUB balance."""

    usd_balance: MoneyValue | None
    """USD balance."""

    eur_balance: MoneyValue | None
    """EUR balance."""

    transactions: TransactionPreviewsBatch | None
    """Transaction previews."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: TransactionsPageParsingOptions | None = None
    ) -> TransactionsPage:
        from funpayparsers.parsers.page_parsers.transactions_page_parser import (
            TransactionsPageParser,
            TransactionsPageParsingOptions,
        )

        options = options or TransactionsPageParsingOptions()
        return TransactionsPageParser(raw_source=raw_source, options=options).parse()
