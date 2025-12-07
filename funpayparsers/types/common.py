from __future__ import annotations


__all__ = (
    'MoneyValue',
    'UserBadge',
    'UserPreview',
    'UserRating',
    'Achievement',
    'CurrentlyViewingOfferInfo',
)

from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import Currency, BadgeType


@dataclass
class MoneyValue(FunPayObject):
    """
    Represents a monetary value with an associated currency.

    This class is used to store money-related information, such as:
        - the price of an offer,
        - the total of an order,
        - the user balance,
        - etc.
    """

    value: int | float
    """The numeric amount of the monetary value."""

    character: str
    """The currency character, e.g., ``'$'``, ``'€'``, ``'₽'``, ``'¤'``, etc."""

    @property
    def currency(self) -> Currency:
        return Currency.get_by_character(self.character)


@dataclass
class UserBadge(FunPayObject):
    """
    Represents a user badge.

    This badge is shown in heading messages sent by support, arbitration,
    or the FunPay issue bot, and also appears on the profile pages of support users.
    """

    text: str
    """Badge text."""

    css_class: str
    """
    The full CSS class of the badge.

    Known values:
        - ``'label-default'`` — FunPay auto delivery bot;
        - ``'label-primary'`` — FunPay system notifications 
            (e.g., new order, order COMPLETED, new review, etc.);
        - ``'label-success'`` — support or arbitration;
        - ``'label-danger'`` - blocked user;

    .. warning:: 
        This field contains the **full** CSS class. To check the badge type,
        use the ``in`` operator instead of ``==``, as the class may include 
        additional modifiers.
    """

    @property
    def type(self) -> BadgeType:
        """Badge type."""

        return BadgeType.get_by_css_class(self.css_class)


@dataclass
class UserPreview(FunPayObject):
    """
    Represents user preview.
    """

    id: int
    """User ID."""

    username: str
    """Username."""

    online: bool
    """True, if user is online."""

    banned: bool
    """True, if user is banned."""

    status_text: str
    """Status text (online / banned / last seen online)."""

    avatar_url: str
    """User avatar URL."""


@dataclass
class UserRating(FunPayObject):
    """
    Represents full user rating.
    """

    stars: float | None
    """Stars amount (if available)."""

    reviews_amount: int
    """Reviews amount."""

    five_star_reviews_percentage: float
    """Five star reviews percentage."""

    four_star_reviews_percentage: float
    """Four star reviews percentage."""

    three_star_reviews_percentage: float
    """Three star reviews percentage."""

    two_star_reviews_percentage: float
    """Two star reviews percentage."""

    one_star_reviews_percentage: float
    """One star reviews percentage."""


@dataclass
class Achievement(FunPayObject):
    """Represents a user achievement."""

    css_class: str
    """The full CSS class of the achievement."""

    text: str
    """Achievement text."""


@dataclass
class CurrentlyViewingOfferInfo(FunPayObject):
    """represents a currently viewing offer info."""

    id: int | str | None
    """Offer ID."""

    title: str | None
    """Offer title."""
