from __future__ import annotations


__all__ = ('MyOffersPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.my_offers_page_parser import MyOffersPageParsingOptions


@dataclass
class MyOffersPage(FunPayPage):
    """Represents personal lots page (`/lots/<subcategory_id>/trade`)."""

    category_id: int | None
    """Category ID (from raise button data-game, if present)."""

    subcategory_id: int
    """Subcategory ID."""

    offers: dict[int | str, OfferPreview]
    """Owned offers mapped by offer ID."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: MyOffersPageParsingOptions | None = None
    ) -> MyOffersPage:
        from funpayparsers.parsers.page_parsers.my_offers_page_parser import (
            MyOffersPageParser,
            MyOffersPageParsingOptions,
        )

        options = options or MyOffersPageParsingOptions()
        return MyOffersPageParser(raw_source=raw_source, options=options).parse()
