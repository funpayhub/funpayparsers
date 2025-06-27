__all__ = ('OrderCounterpartyInfo', 'OrderPreview', 'OrderPreviewsBatch')


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

    banned: bool
    """True, if counterparty is banned."""

    status_text: str
    """Status text (online / banned / last seen online)."""

    avatar_url: str
    """Counterpart avatar URL."""

    def __str__(self):
        return f'{self.username} (id: {self.id}), status: {self.status_text}.'


@dataclass
class OrderPreview(FunPayObject):
    """
    Represents an order preview.
    """

    id: str
    """Order ID."""

    date_text: str
    """Order date (as human-readable text)."""

    desc: str
    """Order description."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    total: MoneyValue
    """Order total."""

    counterparty: OrderCounterpartyInfo
    """Associated counterparty info."""

    def __str__(self):
        return (f'<{self.total} {self.status.name} order {self.id} '
                f'dated {self.date_text}: {self.desc}. ({self.category_text})>')


@dataclass
class OrderPreviewsBatch(FunPayObject):
    """
    Represents a single batch of order previews returned by FunPay.

    This batch contains a portion of all available order previews (typically 100),
    along with metadata required to fetch the next batch.
    """

    orders: list[OrderPreview]
    """List of order previews included in this batch."""

    next_order_id: str | None
    """
    ID of the next order to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch
    the following batch of order previews. If `None`, there are no more orders to load.
    """