from __future__ import annotations


__all__ = ('SubcategoryPage', )

from dataclasses import dataclass

from funpayparsers.types.enums import SubcategoryType
from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.categories import Subcategory
from funpayparsers.types.pages.base import FunPayPage


@dataclass
class SubcategoryPage(FunPayPage):
    """
    Represents a subcategory offers list page
    (`https://funpay.com/<lots/chips>/<subcategory_id>/`)
    """

    category_id: int
    """Subcategory category ID."""

    subcategory_id: int
    """Subcategory ID."""

    subcategory_type: SubcategoryType
    """Subcategory type."""

    related_subcategories: list[Subcategory] | None
    """List of related subcategories (including this one), if exists."""

    offers: list[OfferPreview] | None
    """Subcategory offers list."""
