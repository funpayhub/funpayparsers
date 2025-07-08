__all__ = ('FunPayObjectParser', 'ParsingOptions',
           'FunPayHTMLObjectParser', 'FunPayJSONObjectParser')

from abc import ABC, abstractmethod
from typing import get_args, get_origin
from dataclasses import dataclass, replace, fields, field
from typing import Generic, Type, TypeVar, Any, cast
from collections.abc import Sequence, Mapping
import json

from funpayparsers.types.base import FunPayObject
from funpayparsers.exceptions import ParsingError
from selectolax.lexbor import LexborHTMLParser


R = TypeVar('R', bound=Any)
O = TypeVar('O', bound='ParsingOptions')


@dataclass(frozen=True)
class ParsingOptions:
    """
    Base class for all parser option dataclasses.

    Option instances can be merged using the `&` or `|` operators,
    both of which return a new instance of the current class.

    - `&` merges only the explicitly specified fields from `options2`.
    - `|` merges all fields from `options2`, including those with default values.

    Examples:

        >>> options1 = ParsingOptions(empty_raw_source=True)
        >>> options2 = ParsingOptions(context={"key": "value"})
        >>> options3 = options1 & options2  # Creates a new instance of options1
        >>> options3.empty_raw_source
        True
        >>> options3.context
        {'key': 'value'}

        >>> options1 = ParsingOptions(empty_raw_source=True)
        >>> options2 = ParsingOptions(context={"key": "value"})
        >>> options3 = options1 | options2  # Creates a new instance of options1
        >>> options3.empty_raw_source
        False
        >>> options3.context
        {'key': 'value'}

    Note:
        - Neither operator mutates the original instances.
        - The result is always a new instance of the left-hand operand's class (`options1`).
    """

    empty_raw_source: bool = False
    context: dict[Any, Any] = field(default_factory=dict)

    def __merge_options__(self: O, other, non_explicit: bool = False) -> O:
        self_fields = {i.name: getattr(self, i.name)
                       for i in getattr(self, '__dataclass_fields__', {}).values()}
        other_fields = {i.name: getattr(other, i.name)
                        for i in getattr(other, '__dataclass_fields__', {}).values()}

        other_explicit_fields = getattr(other, '__passed_kwargs__', {})
        for k in self_fields:
            if k in other_fields and (non_explicit or k in other_explicit_fields):
                self_fields[k] = other_fields[k]

        return self.__class__(**self_fields)

    def __and__(self: O, other) -> O:
        return self.__merge_options__(other, non_explicit=False)

    def __or__(self: O, other) -> O:
        return self.__merge_options__(other, non_explicit=True)


def _new(cls: Type[O], *args: Any, **kwargs: Any) -> O:
    instance = cast(O, super(ParsingOptions, cls).__new__(cls))
    super(ParsingOptions, cls).__setattr__(instance, '__passed_args__', args)
    super(ParsingOptions, cls).__setattr__(instance, '__passed_kwargs__', kwargs)
    return instance

setattr(ParsingOptions, '__new__', _new)


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
    __options_cls__: Type[ParsingOptions] | None = None

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

        except Exceptions as e:
            raise ParsingError(raw_source=self.raw_source) from e

    def empty_raw_source(self,
                         obj: FunPayObject | Sequence[Any] | Mapping[Any, Any]) -> None:
        if hasattr(type(obj), '__dataclass_fields__') and isinstance(obj, FunPayObject):
            if hasattr(obj, 'raw_source'):
                setattr(obj, 'raw_source', '')

            for f in fields(obj):
                self.empty_raw_source(getattr(obj, f.name))

        elif isinstance(obj, (list, tuple)):
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
                if isinstance(arg, type) and issubclass(arg, ParsingOptions):
                    return arg
        raise LookupError('No suitable options class found.')


class FunPayHTMLObjectParser(FunPayObjectParser[R, O], ABC):
    def __init__(self, raw_source: str, options: O | None = None, **overrides):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """
        super().__init__(raw_source=raw_source, options=options, **overrides)
        self._tree = None

    @property
    def tree(self) -> LexborHTMLParser:
        if self._tree is not None:
            return self._tree

        self._tree = LexborHTMLParser(self.raw_source)
        return self._tree

    @property
    def raw_source(self) -> str:
        return self._raw_source


class FunPayJSONObjectParser(FunPayObjectParser[R, O], ABC):
    def __init__(self, raw_source: str | dict | list, options: O | None = None, **overrides):
        super().__init__(raw_source=raw_source, options=options, **overrides)
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
