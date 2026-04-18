from __future__ import annotations


__all__ = ('SubcategoryPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.enums import SubcategoryType
from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.categories import Subcategory
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.subcategory_structure import SubcategoryStructure


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.subcategory_page_parser import (
        SubcategoryPageParsingOptions,
    )


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

    structure: SubcategoryStructure | None = None
    """
    Partial subcategory field structure, derived from the listing page's
    ``data-fields`` JSON and per-field form groups.

    This is a strict subset of the authenticated ``offerEdit`` schema:
    listing pages omit non-filterable fields (e.g. ``TEXTAREA``, ``IMAGES``)
    and may render option lists as button groups rather than ``<select>``.

    ``None`` when the page has no ``div.lot-fields`` block (e.g. chips).
    """

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: SubcategoryPageParsingOptions | None = None
    ) -> SubcategoryPage:
        from funpayparsers.parsers.page_parsers.subcategory_page_parser import (
            SubcategoryPageParser,
            SubcategoryPageParsingOptions,
        )

        options = options or SubcategoryPageParsingOptions()
        return SubcategoryPageParser(raw_source=raw_source, options=options).parse()
