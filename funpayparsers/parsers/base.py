__all__ = ('FunPayObjectParser', 'FunPayObjectParserOptions')

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace, fields, asdict
from typing import Generic, Type, TypeVar, Any
from collections.abc import Sequence, Mapping

from lxml import html

from funpayparsers.types.base import FunPayObject


@dataclass(frozen=True)
class FunPayObjectParserOptions:
    """
    Base class for all parser option dataclasses.
    """
    empty_raw_source: bool = False

    def __and__(self, other):
        self_fields = asdict(self)
        other_fields = asdict(other)

        for k in self_fields:
            if k in other_fields:
                self_fields[k] = other_fields[k]

        return self.__class__(**self_fields)



T = TypeVar('T', bound=Any)
P = TypeVar('P', bound=FunPayObjectParserOptions)


class FunPayObjectParser(ABC, Generic[T, P]):
    """
    Base class for all parsers.
    """

    @property
    @abstractmethod
    def __options_cls__(self) -> Type[P]: ...

    def __init__(self, raw_source: str, options: P | None = None, **overrides):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """

        self._raw_source = raw_source
        self._options: P = self._build_options(options, **overrides)
        self._tree = None

    @abstractmethod
    def _parse(self) -> T: ...

    def parse(self) -> T:
        try:
            result = self._parse()

            if self.options.empty_raw_source:
                self.empty_raw_source(result)

            return result

        except Exception as e:
            raise e  # todo: make custom exceptions e.g. ParsingError

    def empty_raw_source(self,
                         obj: FunPayObject |
                              Sequence[FunPayObject] |
                              Mapping[Any, FunPayObject]) -> None:
        if hasattr(type(obj), '__dataclass_fields__'):  # if dataclass
            if hasattr(obj, 'raw_source'):
                setattr(obj, 'raw_source', '')

            for f in fields(obj):
                self.empty_raw_source(getattr(obj, f.name))

        elif isinstance(obj, (list, tuple)):
            for item in obj:
                self.empty_raw_source(item)

        elif isinstance(obj, dict):
            for item in obj.values():
                self.empty_raw_source(item)

    @property
    def tree(self) -> html.HtmlElement:
        if self._tree is not None:
            return self._tree

        self._tree = html.fromstring(self.raw_source)
        return self._tree

    @property
    def raw_source(self) -> str:
        return self._raw_source

    @property
    def options(self) -> P:
        return self._options

    @classmethod
    def _build_options(cls, options: P | None, **overrides) -> P:
        base = options or cls.__options_cls__()
        overrides = {k: v for k, v in overrides.items() if
                     k in getattr(base, '__dataclass_fields__', {})}
        return replace(base, **overrides)
