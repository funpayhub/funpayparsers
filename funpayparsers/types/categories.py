__all__ = ('Category', 'Subcategory')

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

    :warning: Subcategory ID is not always unique. 
    IDs are unique per subcategory type but may repeat across types.
    That means, that some common category (`CategoryType.COMMON`) 
    can have same ID as some currency category (`CategoryType.CURRENCY`).
    
    Example:
        Common category "Lineage 2 Items (RU)" (category ID: 1): https://funpay.com/lots/1/
        Currency category "Lineage 2 Adena (RU)" (category ID: 1): https://funpay.com/chips/1/
    """

    name: str
    """Subcategory name."""

    type: SubcategoryType
    """Subcategory type."""
