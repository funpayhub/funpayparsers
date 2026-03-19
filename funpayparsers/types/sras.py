from __future__ import annotations


__all__ = ('SrasSectionRestriction',)

from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import SubcategoryType


@dataclass
class SrasSectionRestriction(FunPayObject):
    """Represents a SRAS restriction for a specific subcategory."""

    subcategory_id: int
    """Subcategory ID."""

    subcategory_type: SubcategoryType
    """Subcategory type."""

    max_rating: int
    """Maximum allowed seller rating in this subcategory."""
