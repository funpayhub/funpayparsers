__all__ = ('OrderCounterpartyInfo', 'OrderPreview')


from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.enums import OrderStatus


@dataclass
class OrderCounterpartyInfo(FunPayObject):
    """
    Represents an order counterparty details.

    Represents the other participant of the order
    (buyer or seller, depending on the context).
    """

    id: int
    """Counterparty ID."""

    username: str
    """Counterparty username."""

    online: bool
    """True, if counterparty is online."""

    blocked: bool
    """True, if counterparty is blocked."""

    last_online_text: str | None
    """Last online status text (if available)."""

    avatar_url: str
    """Counterpart avatar URL."""


@dataclass
class OrderPreview(FunPayObject):
    """
    Represents an order preview.
    Order previews can be found on sells or purchases pages.
    """

    id: str
    """Order ID."""

    date_text: str
    """Order date (as human-readable text)."""

    desc: str | None
    """Order description (if available)."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    amount: MoneyValue
    """Order amount."""

    counterparty: OrderCounterpartyInfo
    """Associated counterparty info."""
