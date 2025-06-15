from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import SubcategoryType


@dataclass
class Category(FunPayObject):
    """
    Represents a category from FunPay main page.
    """

    name: str
    """Category name."""

    subcategories: list['Subcategory']
    """List of subcategories."""


@dataclass
class Subcategory(FunPayObject):
    """
    Represents a subcategory from FunPay main page.
    """

    id: int
    """
    Subcategory ID.

    :warning: Subcategory ID is not unique. 
    IDs are unique per subcategory type but may repeat across types.
    """

    name: str
    """Subcategory name."""

    type: SubcategoryType
    """Subcategory type."""
