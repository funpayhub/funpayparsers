__all__ = ('MoneyValue', 'UserBadge')


from typing import Literal
from dataclasses import dataclass
from .base import FunPayObject
from .enums import Currency


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

    currency: Currency
    """The currency of the value."""


@dataclass
class UserBadge(FunPayObject):
    """
    Represents a user badge.

    This badge is shown in heading messages sent by support, arbitration, or the FunPay auto-issue bot,
    and also appears on the profile pages of support users.
    """

    text: str
    """Badge text."""

    css_class: str
    """
    The full CSS class of the badge.

    Known values:
        - `label-default` — FunPay auto-issue bot
        - `label-primary` — FunPay system notifications (e.g., new order, order completed, new review, etc.)
        - `label-success` — Support or arbitration

    **WARNING**: This field contains the **full** CSS class. To check the badge type,
    use the `in` operator rather than `==`, as the class may include additional modifiers.
    """
