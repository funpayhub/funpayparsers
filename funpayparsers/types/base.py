from __future__ import annotations


__all__ = ('FunPayObject',)

from typing import TYPE_CHECKING, Any, Type, TypeVar
from dataclasses import field, asdict, dataclass


if TYPE_CHECKING:
    pass


SelfT = TypeVar('SelfT', bound='FunPayObject')


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

    @classmethod
    def from_raw_source(cls: type[SelfT], raw_source: str, options: Any = None) -> SelfT:
        """
        Create instance from a raw source using related parser.
        """
        raise NotImplementedError(f'{cls.__name__}.from_raw_source is not implemented.')
