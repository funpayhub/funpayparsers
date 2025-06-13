__all__ = ('OrderCounterpartyInfo', 'OrderPreview')


from dataclasses import dataclass
from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import OrderStatus
from funpayparsers.types.common import MoneyValue


@dataclass
class OrderCounterpartyInfo(FunPayObject):
    id: int
    """Counterparty user id."""

    username: str
    """Counterparty user username."""

    online: bool
    """Whether the counterparty is online."""

    blocked: bool
    """Whether the counterparty is blocked."""

    last_online_text: str | None
    """Last online text of the counterparty (if exists)."""

    avatar_url: str
    """Counterpart avatar url."""



@dataclass
class OrderPreview(FunPayObject):
    """
    Represents an order preview.
    """

    id: str
    """Order ID."""

    date_text: str
    """Order date text."""

    desc: str | None
    """Order description (if exists)."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    amount: MoneyValue
    """Order amount."""

    counterparty: OrderCounterpartyInfo
    """Order counterpart info."""
