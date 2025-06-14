__all__ = ('Review',)


from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue


@dataclass
class Review(FunPayObject):
    """
    Represents a review.
    Reviews can be found on sellers page or on order page.

    :note: This DC doesn't include a field for the reviews visibility for 2 reasons:

    1. Reviews appear in two contexts: on seller pages (public)
        and on private order detail pages (visible only to the involved parties).
        Visibility status is only available on private order pages.
        For consistency, the field was omitted.

    2. The HTML structure of reviews is identical in both cases,
        while the visibility flag is located outside the review block.
        Therefore, visibility status is handled in the dataclass representing
        the private order page.
    """

    rating: int | None
    """Review rating (stars amount)."""

    text: str | None
    """Review text."""

    order_total: MoneyValue | None
    """Order total amount (price) associated with this review."""

    order_category: str | None
    """Order category name associated with this review."""

    sender_username: str | None
    """Order sender username."""

    sender_id: int | None
    """Order sender ID."""

    sender_avatar_url: str | None
    """Order sender avatar URL."""

    order_id: str | None
    """Order ID associated with this review."""

    order_time_string: str | None
    """Order time string associated with this review."""

    response: str | None
    """Sellers response to this review."""
