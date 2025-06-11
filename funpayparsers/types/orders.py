__all__ = ('OrderCounterpartyInfo', 'OrderPreview')


from dataclasses import dataclass
from .base import FunPayObject
from .enums import OrderStatus
from .common import MoneyValue


@dataclass
class OrderCounterpartyInfo(FunPayObject):
    id: int
    nickname: str
    online: bool
    photo: str



@dataclass
class OrderPreview(FunPayObject):
    id: int
    date: str
    desc: str
    category_text: str
    status: OrderStatus
    value: MoneyValue
    counterparty: None
