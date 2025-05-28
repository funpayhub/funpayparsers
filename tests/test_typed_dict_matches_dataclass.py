from funpayparsers import types as funpay_types
from funpayparsers.types import FunPayObject
from typing import get_origin, get_args, TypedDict, Type, ForwardRef
from types import get_original_bases
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
    bases = get_original_bases(funpay_object)
    for base in bases:
        origin = get_origin(base)
        if not issubclass(origin, FunPayObject):
            continue

        args = get_args(base)
        if len(args) != 1:
            return None

        generic_type = args[0]
        if isinstance(generic_type, ForwardRef):
            generic_type = generic_type._evaluate(globalns=getattr(funpay_types, '__dict__', {}),
                                                  localns=locals(), recursive_guard=frozenset())

        if inspect.isclass(generic_type) and isinstance(generic_type, type(TypedDict("Dummy", {}))):
            return generic_type
    return None


def compare_td_and_dc_annotations(dataclass: Type[FunPayObject],
                                  td_annotations, dc_annotations) -> set:
    """
    Compares nested FunPayObject-typed fields between a dataclass and its corresponding TypedDict.

    This function checks only the fields in the dataclass whose types are subclasses of FunPayObject.
    For each such field, it retrieves the TypedDict used as the generic parameter for the corresponding
    FunPayObject subclass and compares it with the field type declared in the parent TypedDict (i.e.,
    the one used as the generic type argument for the 'outer' dataclass).

    :param dataclass: The dataclass subclass of FunPayObject being checked.
    :param td_annotations: A dictionary of annotations from the TypedDict used as the dataclass's generic parameter.
    :param dc_annotations: A dictionary of field types from the dataclass itself.
    :return: A set of field names that were checked for FunPayObject-type consistency.
    """
    checked_annotations = set()

    for field, type_ in dc_annotations.items():
        if not inspect.isclass(type_) or not issubclass(type_, FunPayObject):
            continue

        field_type_generic_td = get_typed_dict_class(type_)
        assert field_type_generic_td is not None, (
            f'Missing required TypedDict generic type parameter in '
            f'{type_.__module__}.{type_.__qualname__} declaration.'
        )

        assert field_type_generic_td is td_annotations.get(field, None), (
            f'Incorrect TypedDict used as a generic argument in class '
            f'{type_.__module__}.{type_.__qualname__} '
            f'which is the type of {dataclass.__module__}.{dataclass.__qualname__}.{field}:\n'
            f'  Expected: {td_annotations.get(field, None)}\n'
            f'  Found: {field_type_generic_td}'
        )

        checked_annotations.add(field)
    return checked_annotations



class TestTypedDictsMatchesDataclasses(unittest.TestCase):
    def test_typed_dicts_matches_dataclasses(self):
        for name, class_ in vars(funpay_types).items():
            if not inspect.isclass(class_) or class_ is FunPayObject or not issubclass(class_, FunPayObject):
                continue

            generic_typed_dict = get_typed_dict_class(class_)
            assert generic_typed_dict is not None, (
                f'Missing required TypedDict generic type parameter in '
                f'{class_.__module__}.{class_.__qualname__} declaration.'
            )

            td_annotations = getattr(generic_typed_dict, '__annotations__', {})
            dc_annotations = {k: v.type for k, v in getattr(class_, '__dataclass_fields__').items()}
            checked_annotations = compare_td_and_dc_annotations(class_, td_annotations, dc_annotations)

            assert ({k: td_annotations[k] for k in td_annotations.keys() - checked_annotations} ==
                    {k: dc_annotations[k] for k in dc_annotations.keys() - checked_annotations}), (
                f'Mismatch in fields definitions for {name}:\n'
                f'    {class_.__module__}.{class_.__qualname__}: {dc_annotations}\n'
                f'    {generic_typed_dict.__module__}.{generic_typed_dict.__qualname__}: {td_annotations}'
            )
