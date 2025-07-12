from __future__ import annotations


__all__ = ('FunPayObject',)

from typing import Any, Type, TypeVar
from dataclasses import asdict, dataclass, field


SelfT = TypeVar('SelfT', bound='FunPayObject[Any]')


@dataclass
class FunPayObject:
    """Base class for all FunPay-parsed objects."""

    raw_source: str = field(compare=False)
    """
    Raw source of an object.
    Typically a HTML string, but in rare cases can be a JSON string.
    """

    def as_dict(self) -> dict[str, Any]:
        """
        Returns a dict representations of an instance.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls: Type[SelfT], data: dict[str, Any]) -> SelfT:
        """
        Creates instance from a dict.
        """
        return cls(**data)
