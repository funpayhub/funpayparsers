__all__ = ('LotPreview', 'LotSeller')

from dataclasses import dataclass
from typing import Literal

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue


@dataclass
class LotSeller(FunPayObject):
    """
    Represents the seller of a lot.

    Used in lot previews.
    """

    id: int
    """The seller's user ID."""

    username: str
    """The seller's username."""

    online: bool
    """Whether the seller is currently online."""

    avatar_url: str
    """URL of the seller's avatar."""

    register_date_text: str
    """The seller's registration date (as a formatted string)."""

    rating: Literal[0, 1, 2, 3, 4, 5]
    """The seller's rating (number of stars)."""

    reviews_amount: int
    """The total number of reviews received by the seller."""


@dataclass
class LotPreview(FunPayObject):
    """
    Represents a lot preview.
    """

    id: int | str
    """Unique lot ID."""

    auto_issue: bool
    """Whether auto-issue is enabled for this lot."""

    is_pinned: bool
    """Whether this lot is pinned to the top of the list."""

    server_id: int | None
    """The ID of the server associated with the lot, if applicable."""

    server_name: str | None
    """The name of the server associated with the lot, if applicable."""

    desc: str | None
    """The description of the lot, if provided."""

    amount: int | None
    """The quantity of goods available in this lot, if specified."""

    price: MoneyValue
    """The price of the lot."""

    seller: LotSeller
    """Information about the seller of the lot."""

    other_data: dict[str, str]
    """
    Additional data related to the lot, such as server ID, side ID, etc., 
        if applicable.
    """

    other_data_names: dict[str, str]
    """
    Human-readable names corresponding to entries in `other_data`, if applicable.
    Not all entries, that are exists in other_data can be found here.
    """
