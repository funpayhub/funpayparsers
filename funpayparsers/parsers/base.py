__all__ = ('FunPayObjectParser',)

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Generic, Type, TypeVar

from lxml import html

from funpayparsers.types.base import FunPayObject

T = TypeVar('T', bound=FunPayObject)
P = TypeVar('P', bound='FunPayObjectParserOptions')


@dataclass
class FunPayObjectParserOptions:
    """
    Base class for all parser option dataclasses.
    """
    ...


class FunPayObjectParser(ABC, Generic[T, P]):
    """
    Base class for all parsers.
    """

    options_cls: Type[P] = FunPayObjectParserOptions

    def __init__(self, raw_source: str, options: P | None, **overrides):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """
        self.raw_source = raw_source
        self.options = self._build_options(options, **overrides)
        self._tree = None

    @abstractmethod
    def parse(self) -> T: ...

    @property
    def tree(self):
        if self._tree is not None:
            return self._tree

        self._tree = html.fromstring(self.raw_source)
        return self._tree

    @classmethod
    def _build_options(cls, options: P | None, **overrides) -> P:
        base = options or cls.options_cls()
        overrides = {k: v for k, v in overrides.items() if k in
                     getattr(base, '__dataclass_fields__', {})}
        return replace(base, **overrides)
