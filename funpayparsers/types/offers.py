__all__ = ('OfferPreview', 'OfferSeller', 'OfferFields')

from dataclasses import dataclass, field

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue


@dataclass
class OfferSeller(FunPayObject):
    """
    Represents the seller of an offer.
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

    rating: int
    """The seller's rating (number of stars)."""

    reviews_amount: int
    """The total number of reviews received by the seller."""


@dataclass
class OfferPreview(FunPayObject):
    """
    Represents an offer preview.
    """

    id: int | str
    """Unique offer ID."""

    auto_issue: bool
    """Whether auto-issue is enabled for this offer."""

    is_pinned: bool
    """Whether this offer is pinned to the top of the list."""

    desc: str | None
    """The description of the offer, if provided."""

    amount: int | None
    """The quantity of goods available in this offer, if specified."""

    price: MoneyValue
    """The price of the offer."""

    seller: OfferSeller | None
    """Information about the offer seller, if applicable."""

    other_data: dict[str, str | int]
    """
    Additional data related to the offer, such as server ID, side ID, etc., 
        if applicable.
    """

    other_data_names: dict[str, str]
    """
    Human-readable names corresponding to entries in `other_data`, if applicable.
    Not all entries, that are exists in other_data can be found here.
    """



@dataclass
class OfferFields(FunPayObject):
    """
    Represents the offer fields.
    """

    csrf_token: str
    """User CSRF token."""

    other_fields: dict[str, str | int] = field(default_factory=dict)
    """Other offer fields."""
