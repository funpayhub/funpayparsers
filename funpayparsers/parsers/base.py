__all__ = ('FunPayHTMLObjectParser', 'FunPayObjectParserOptions')

from abc import ABC, abstractmethod
from typing import get_args, get_origin
from dataclasses import dataclass, replace, fields, asdict, field
from typing import Generic, Type, TypeVar, Any
from collections.abc import Sequence, Mapping

from lxml import html
import json

from funpayparsers.types.base import FunPayObject


@dataclass(frozen=True)
class FunPayObjectParserOptions:
    """
    Base class for all parser option dataclasses.
    """
    empty_raw_source: bool = False
    context: dict[Any, Any] = field(default_factory=dict)

    def __and__(self, other):
        self_fields = asdict(self)
        other_fields = asdict(other)

        for k in self_fields:
            if k in other_fields:
                self_fields[k] = other_fields[k]

        return self.__class__(**self_fields)



R = TypeVar('R', bound=Any)
O = TypeVar('O', bound=FunPayObjectParserOptions)


class FunPayObjectParser(ABC, Generic[R, O]):
    """
    Base class for all parsers.

    Note:
        You should not inherit from this class directly, unless you are implementing a new type of parsers
        (e.g., `FunPayXMLObjectParser` or `FunPayYAMLObjectParser`).

        For most use cases, such as parsing FunPay objects, inherit from
        `FunPayHTMLObjectParser` (for HTML sources) or
        `FunPayJSONObjectParser` (for JSON-string/python collection sources)
    """
    __options_cls__: Type[FunPayObjectParserOptions] | None = None

    def __init__(self, raw_source: Any, options: O | None = None, **overrides):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """
        self._raw_source = raw_source
        self._options: O = self._build_options(options, **overrides)

    @abstractmethod
    def _parse(self) -> R: ...

    def parse(self) -> R:
        try:
            result = self._parse()

            if self.options.empty_raw_source:
                self.empty_raw_source(result)

            return result

        except Exception as e:
            raise e  # todo: make custom exceptions e.g. ParsingError

    def empty_raw_source(self,
                         obj: FunPayObject | Sequence[Any] | Mapping[Any, Any]) -> None:
        if hasattr(type(obj), '__dataclass_fields__'):
            if hasattr(obj, 'raw_source'):
                setattr(obj, 'raw_source', '')

            for f in fields(obj):
                self.empty_raw_source(getattr(obj, f.name))

        elif isinstance(obj, Sequence):
            for item in obj:
                self.empty_raw_source(item)

        elif isinstance(obj, Mapping):
            for item in obj.values():
                self.empty_raw_source(item)

    @property
    def raw_source(self) -> Any:
        return self._raw_source

    @property
    def options(self) -> O:
        return self._options

    @classmethod
    def _build_options(cls, options: O | None, **overrides) -> O:
        base = options or cls.get_options_cls()()
        overrides = {k: v for k, v in overrides.items() if
                     k in getattr(base, '__dataclass_fields__', {})}
        return replace(base, **overrides)

    @classmethod
    def get_options_cls(cls) -> Type[O]:
        if cls.__options_cls__ is not None:
            return cls.__options_cls__

        try:
            return cls._get_options_cls_inner()
        except Exception as e:
            raise LookupError(f'Unable to determine options class for `{cls.__name__}`.\n'
                              f'This can happen with complicated inheritance.\n'
                              f'Try explicitly specifying `__options_cls__` in `{cls.__name__}`.') from e

    @classmethod
    def _get_options_cls_inner(cls) -> Type[O]:
        parents = getattr(cls, '__orig_bases__', ())
        for parent in parents:
            origin, args = get_origin(parent), get_args(parent)
            if origin is None or not issubclass(origin, FunPayObjectParser):
                continue

            if not args:
                return origin.get_options_cls()

            for arg in args:
                if isinstance(arg, type) and issubclass(arg, FunPayObjectParserOptions):
                    return arg
        raise LookupError('No suitable options class found.')


class FunPayHTMLObjectParser(FunPayObjectParser[R, O], ABC):
    def __init__(self, raw_source: str, options: O | None = None, **overrides):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """
        super().__init__(raw_source=raw_source,
                         options=options,
                         **overrides)

        self._tree = None

    @property
    def tree(self) -> html.HtmlElement:
        if self._tree is not None:
            return self._tree

        self._tree = html.fromstring(self.raw_source)
        return self._tree

    @property
    def raw_source(self) -> str:
        return self._raw_source


class FunPayJSONObjectParser(FunPayHTMLObjectParser[R, O], ABC):
    def __init__(self, raw_source: str | dict | list, options: O | None = None, **overrides):
        super().__init__(raw_source=raw_source,
                         options=options,
                         **overrides)
        self._data = None

    @property
    def data(self) -> dict[str, Any] | list[Any]:
        if self._data is not None:
            return self._data

        self._data = json.loads(self.raw_source) if isinstance(self.raw_source, str) else self.raw_source
        return self._data

    @property
    def raw_source(self) -> str | dict | list:
        return self._raw_source
