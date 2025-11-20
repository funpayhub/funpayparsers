from __future__ import annotations


__all__ = ('Review', 'ReviewsBatch')


from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue


@dataclass
class Review(FunPayObject):
    """
    Represents a review.

    Reviews can be found on the seller’s page or on the order detail page.

    .. note::
        This dataclass does not include a field for review visibility for two reasons:

        1. Reviews appear in two contexts: on seller pages (public)
           and on private order detail pages (visible only to the involved parties).
           Visibility status is available only on private order pages.
           To maintain consistency, this field was omitted.

        2. The HTML structure of reviews is almost identical in both contexts,
           while the visibility flag is located outside the review’s main div.
           Therefore, visibility is handled in the dataclass representing
           the order page (``funpayparsers.types.pages.OrderPage``).
    """

    rating: int | None
    """Review rating (stars amount)."""

    text: str | None
    """Review text."""

    order_total: MoneyValue | None
    """
    Approximate total amount of the order this review refers to.

    .. note::
        This value may be significantly rounded and should be considered
        only as an estimate, not the exact order total.
    """

    category_str: str | None
    """Category name of the order this review refers to."""

    sender_username: str | None
    """
    Review sender username.
    """

    sender_id: int | None
    """Review sender ID."""

    sender_avatar_url: str | None
    """Review sender avatar URL."""

    order_id: str | None
    """Order ID associated with this review."""

    date_text: str | None
    """
    Human-readable relative timestamp indicating when the order that review refers to 
    was made.
    
    Examples: `2 months ago`, `3 years ago`, etc. (depends on selected language).
    """

    reply: str | None
    """Sellers reply to this review."""

    @property
    def timestamp(self) -> int:
        """
        Review timestamp.

        Available only for owned reviews (from your profile page or that has been written by you).

        ``0``, if an error occurred while parsing.
        """
        from funpayparsers.parsers.utils import parse_date_string

        if self.date_text is None:
            return 0
        try:
            return parse_date_string(self.date_text)
        except ValueError:
            return 0


@dataclass
class ReviewsBatch(FunPayObject):
    """
    Represents a single batch of reviews.

    This batch contains a portion of all available reviews (typically 25),
    along with metadata required to fetch the next batch.
    """

    reviews: list[Review]
    """List of reviews included in this batch."""

    user_id: int | None
    """
    ID of the user to whom all reviews in this batch belong.

    In other words, this is the profile or seller being reviewed,
    not the individual authors of each review.
    """

    filter: str | None
    """
    The current filter applied to the review list.
    
    Known values:
        - ``''`` (empty string): no filter applied
        - ``'1'`` to ``'5'``: filters reviews by the given star rating
    """

    next_review_id: str | None
    """
    ID of the next review to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch
    the following batch of reviews. If ``None``, there are no more reviews to load.
    """
