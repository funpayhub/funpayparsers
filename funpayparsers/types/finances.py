__all__ = ('TransactionPreview', )


from dataclasses import dataclass
from .base import FunPayObject
from .common import MoneyValue


@dataclass
class TransactionPreview(FunPayObject):
    id: int
    date_text: str
    desc: str
    status: str  # todo: add enum
    value: MoneyValue
    payment_method: str | None  # todo: add enum
    payment_number: str | None


@dataclass
class Transaction(FunPayObject):
    ...   # todo


