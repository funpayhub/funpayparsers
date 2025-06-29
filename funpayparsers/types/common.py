__all__ = ('MoneyValue', 'UserBadge', 'CurrentlyViewingOfferInfo')

from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import Currency, BadgeType


@dataclass
class MoneyValue(FunPayObject):
    """
    Represents a monetary value with an associated currency.

    This class is used to store money-related information, such as:
    - the price of a lot,
    - the total of an order,
    - the user balance,
    - etc.
    """

    value: int | float
    """The numeric amount of the monetary value."""

    character: str
    """The currency character, e.g., $, €, ₽, ¤, etc."""

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
        - `label-default` — FunPay auto-issue bot;
        - `label-primary` — FunPay system notifications 
            (e.g., new order, order COMPLETED, new review, etc.);
        - `label-success` — support or arbitration;
        - `label-danger` - blocked user;

    **WARNING**: This field contains the **full** CSS class. To check the badge type,
        use the `in` operator rather than `==`, as the class may include 
        additional modifiers.
    """

    @property
    def type(self) -> BadgeType:
        """Badge type."""

        return BadgeType.get_by_css_class(self.css_class)

@dataclass
class CurrentlyViewingOfferInfo(FunPayObject):
    id: int | str
    name: str
