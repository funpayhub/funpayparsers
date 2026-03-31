from __future__ import annotations


__all__ = ('OrderPreview', 'OrderPreviewsBatch')


from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import OrderStatus, SubcategoryType
from funpayparsers.types.common import MoneyValue


if TYPE_CHECKING:
    from funpayparsers.types.common import UserPreview
    from funpayparsers.types.subcategory_structure import SubcategoryStructure


@dataclass
class OrderPreview(FunPayObject):
    """Represents an order preview."""

    id: str
    """Order ID."""

    date_text: str
    """Order date (as human-readable text)."""

    title: str
    """Order title."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    total: MoneyValue
    """Order total."""

    counterparty: UserPreview
    """Associated counterparty info."""

    quantity: int = 1
    """
    Number of units ordered.

    Parsed from the ``N шт.`` token in the title (second-to-last comma-separated
    part).  Defaults to ``1`` when the token is absent.
    """

    recipient: str | None = None
    """
    Free-text value entered by the buyer as the delivery target (e.g. a username,
    phone number, email, or any other identifier).

    Always the last comma-separated part of the title, stored as-is without
    any normalisation.  ``None`` when the title has fewer than two parts.
    """

    subcategory_id: int | None = None
    """ID of the subcategory this order belongs to, if known."""

    subcategory_type: SubcategoryType | None = None
    """Type of the subcategory (OFFERS/CHIPS), if known."""

    def parse_title_fields(self, structure: SubcategoryStructure) -> dict[str, str | int]:
        """
        Parse field values from the offer-title portion using the given subcategory structure.

        Strips the order-specific suffix (``recipient`` and, when ``quantity > 1``,
        the ``N шт.`` token) before applying structure-based parsing, so the result
        is equivalent to calling ``parse_title_fields`` on the matching ``OfferPreview``.

        Returns a mapping of field ID → value.  ``NUMERIC_RANGE`` fields are
        returned as ``int``.
        """
        parts = self.title.split(', ')
        strip = 1 + (1 if self.quantity > 1 else 0)
        offer_title = ', '.join(parts[:-strip]) if strip < len(parts) else ''
        if not offer_title:
            return {}
        from funpayparsers.types.subcategory_structure import _parse_title_fields
        return _parse_title_fields(offer_title, structure)

    @property
    def timestamp(self) -> int:
        """
        Order timestamp.

        ``0``, if an error occurred while parsing.
        """
        from funpayparsers.parsers.utils import parse_date_string

        try:
            return parse_date_string(self.date_text)
        except ValueError:
            return 0


@dataclass
class OrderPreviewsBatch(FunPayObject):
    """
    Represents a single batch of order previews.

    This batch contains a portion of all available order previews (typically 100),
    along with metadata required to fetch the next batch.
    """

    orders: list[OrderPreview]
    """List of order previews included in this batch."""

    next_order_id: str | None
    """
    ID of the next order to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch the 
    following batch of order previews. 
    
    If ``None``, there are no more orders to load.
    """
