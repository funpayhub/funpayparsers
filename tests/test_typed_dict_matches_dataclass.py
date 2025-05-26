from funpayparsers import types as funpay_types
from funpayparsers.types import FunPayObject
from typing import get_origin, get_args, TypedDict, Type, _TypedDictMeta
import unittest
import inspect


def get_typed_dict_class(funpay_object: Type[FunPayObject]) -> Type[TypedDict] | None:
    """
    Retrieves the TypedDict class used as a generic type argument for a given FunPayObject subclass.

    For example, given the following classes:
        class MyDict(TypedDict):
            ...

        class MyObject(FunPayObject[MyDict]):
            ...

    Calling get_typed_dict_class(MyObject) will return MyDict.

    :param funpay_object: A subclass of FunPayObject that uses a TypedDict as a generic parameter.
    :return: The TypedDict class used as the type argument, or None if not found.
    """
    bases = getattr(funpay_object, '__orig_bases__', [])
    for base in bases:
        origin = get_origin(base)
        if not issubclass(origin, FunPayObject):
            continue

        args = get_args(base)
        if len(args) == 1 and inspect.isclass(args[0]) and isinstance(args[0], _TypedDictMeta):
            return args[0]
    return None


class TestTypedDictsMatchesDataclasses(unittest.TestCase):
    def test_typed_dicts_matches_dataclasses(self):
        for object_name, funpay_object in vars(funpay_types).items():
            if not inspect.isclass(funpay_object) or funpay_object is FunPayObject or not issubclass(funpay_object, FunPayObject):
                continue

            typed_dict = get_typed_dict_class(funpay_object)
            assert typed_dict is not None, (
                f'Missing required TypedDict generic type parameter in '
                f'{funpay_object.__module__}.{funpay_object.__name__} declaration.'
            )

            typed_dict_annotations = getattr(typed_dict, '__annotations__', {})
            dataclass_annotations = {k: v.type for k, v in getattr(funpay_object, '__dataclass_fields__').items()}


            assert typed_dict_annotations == dataclass_annotations, (
                f'Mismatch in fields definitions for {object_name}:\n'
                f'    {funpay_object.__module__}.{funpay_object.__name__}: {dataclass_annotations}\n'
                f'    {typed_dict.__module__}.{typed_dict.__name__}: {typed_dict_annotations}'
            )
