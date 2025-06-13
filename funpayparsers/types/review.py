__all__ = ('Review', )


from dataclasses import dataclass
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.base import FunPayObject


@dataclass
class Review(FunPayObject):
    """
    Represents a review.
    Reviews can be found on sellers page or on order page.
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