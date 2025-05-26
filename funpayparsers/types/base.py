__all__ = ('FunPayObjectStructure', 'FunPayObject')

from dataclasses import dataclass, asdict
from collections.abc import Mapping
from typing import TypedDict, TypeVar, Type, Generic, cast, Any


SelfT = TypeVar('SelfT', bound='FunPayObject[Any]')
DictT = TypeVar('DictT', bound=Mapping[str, Any])
FunPayObjectStructureT = TypeVar('FunPayObjectStructureT', bound='FunPayObjectStructure')


class FunPayObjectStructure(TypedDict):
    """
    TypedDict describing the dictionary structure used for serialization
    and deserialization of FunPayObject instances and their subclasses.

    Each subclass of FunPayObject must have a corresponding TypedDict
    that precisely matches its fields.

    Those TypedDicts are used as a generic parameter when inheriting from FunPayObject,
    ensuring strict type checking and providing accurate type hints
    for the input and output of `FunPayObject.from_dict` and `FunPayObject.as_dict` methods.
    """
    raw_source: str


@dataclass
class FunPayObject(Generic[FunPayObjectStructureT]):
    """
    Base class for all FunPay-parsed objects.

    Each subclass must specify a corresponding TypedDict (that precisely matches its fields) as a generic parameter,
    which describes the dictionary structure used for serialization and deserialization.

    This guarantees synchronization and type safety between the dataclass fields
    and their dictionary representation, thereby ensuring correct type hints.
    """
    raw_source: str

    def as_dict(self) -> DictT:
        return cast(DictT, asdict(self))

    @classmethod
    def from_dict(cls: Type[SelfT], data: DictT) -> SelfT:
        return cls(**data)  # type: ignore[arg-type]
