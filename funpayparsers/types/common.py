__all__ = ('MoneyValueStructure', 'MoneyValue')


from typing import Literal
from dataclasses import dataclass
from .base import FunPayObject, FunPayObjectStructure


class MoneyValueStructure(FunPayObjectStructure):
    value: int | float
    currency: Literal['USD', 'EUR', 'RUB', 'UAH', 'UNK']


@dataclass
class MoneyValue(FunPayObject[MoneyValueStructure]):
    value: int | float
    currency: Literal['USD', 'EUR', 'RUB', 'UAH', 'UNK']
