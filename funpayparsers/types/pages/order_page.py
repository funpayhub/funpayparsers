__all__ = ('OrderPage', )

from dataclasses import dataclass
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.enums import OrderStatus
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.reviews import Review
from funpayparsers.types.chat import Chat
import re


@dataclass
class OrderPage(FunPayPage):
    """
    Represents an order page (`https://funpay.com/orders/<order_id>/`).
    """

    order_id: str
    """Order ID."""

    order_status: OrderStatus
    """Order status."""

    order_total: MoneyValue
    """Order total."""

    delivered_goods: list[str] | None
    """List of delivered goods."""

    images: list[str] | None
    """List of attached images."""

    order_category_name: str
    """Order category name."""

    order_subcategory_name: str
    """Order subcategory name."""

    order_subcategory_id: int
    """Order subcategory id."""

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
        return int(re.search(r'\d+', amount_str).group())

    @property
    def opened_date_str(self) -> str | None:
        date_str = self._first_found(['open', 'открыт', 'відкрито'])
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def closed_date_str(self) -> str | None:
        date_str = self._first_found(['closed', 'закрыт', 'закрито'])
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

