__all__ = ('OrderStatus', 'Currency')


from enum import Enum


class OrderStatus(Enum):
    PAID = 0
    COMPLETE = 1
    REFUNDED = 2


class Currency(Enum):
    UNK = 0
    RUB = 1
    USD = 2
    EUR = 3
    UAH = 4


