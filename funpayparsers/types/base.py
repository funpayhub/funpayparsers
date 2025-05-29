__all__ = ('FunPayObject', )

from dataclasses import dataclass, asdict
from typing import TypeVar, Type, Any


SelfT = TypeVar('SelfT', bound='FunPayObject[Any]')


@dataclass
class FunPayObject:
    """
    Base class for all FunPay-parsed objects.
    """
    raw_source: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls: Type[SelfT], data: dict[str, Any]) -> SelfT:
        return cls(**data)
