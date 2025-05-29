__all__ = ('MoneyValue', )


from typing import Literal
from dataclasses import dataclass
from .base import FunPayObject


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

    currency: Literal['USD', 'EUR', 'RUB', 'UAH', 'UNK']
    """The currency of the value. 'UNK' is used for unknown currency."""

