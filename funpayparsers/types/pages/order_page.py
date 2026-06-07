from __future__ import annotations


__all__ = ('OrderPage',)

import re
from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.chat import Chat
from funpayparsers.types.enums import OrderStatus, SubcategoryType
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.utils import parse_money_value_string
from funpayparsers.types.reviews import Review
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.order_page_parser import OrderPageParsingOptions


@dataclass
class OrderPage(FunPayPage):
    """Represents an order page (`https://funpay.com/orders/<order_id>/`)."""

    order_id: str
    """Order ID."""

    order_status: OrderStatus
    """Order status."""

    delivered_goods: list[str] | None
    """List of delivered goods."""

    images: list[str] | None
    """List of attached images."""

    order_subcategory_id: int
    """Order subcategory id."""

    order_subcategory_type: SubcategoryType
    """Order subcategory type."""

    data: dict[str, str]
    """Order data (short description, full description, etc.)"""

    review: Review | None
    """Order review."""

    chat: Chat
    """Chat with counterparty."""

    def _first_found(self, names: list[str]) -> str | None:
        for i in names:
            if self.data.get(i) is not None:
                return self.data[i]
        return None

    @property
    def short_description(self) -> str | None:
        """Order short description (title)."""

        return self._first_found(['short description', 'краткое описание', 'короткий опис'])

    @property
    def full_description(self) -> str | None:
        """Order full description (detailed description)."""

        return self._first_found(['detailed description', 'подробное описание', 'докладний опис'])

    @property
    def amount(self) -> int | None:
        amount_str = self._first_found(['amount', 'количество', 'кількість'])
        if not amount_str:
            return None
        return int(re.search(r'\d+', amount_str).group())  # type: ignore[union-attr]
        # always has \d+

    @property
    def open_date_text(self) -> str | None:
        """Order open date."""

        date_str = self._first_found(['open', 'открыт', 'відкрито'])
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def close_date_text(self) -> str | None:
        """Order close date."""

        date_str = self._first_found(['closed', 'закрыт', 'закрито'])
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def order_category_name(self) -> str | None:
        """Order category name."""

        return self._first_found(['game', 'игра', 'гра'])

    @property
    def order_subcategory_name(self) -> str | None:
        """Order subcategory name."""

        return self._first_found(['category', 'категория', 'категорія'])

    @property
    def order_total(self) -> MoneyValue | None:
        """Order total."""

        value = self._first_found(['total', 'сумма', 'сума'])
        if not value:
            return None
        return parse_money_value_string(value)

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: OrderPageParsingOptions | None = None
    ) -> OrderPage:
        from funpayparsers.parsers.page_parsers.order_page_parser import (
            OrderPageParser,
            OrderPageParsingOptions,
        )

        options = options or OrderPageParsingOptions()
        return OrderPageParser(raw_source=raw_source, options=options).parse()
