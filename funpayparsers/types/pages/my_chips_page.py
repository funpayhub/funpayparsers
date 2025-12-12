from __future__ import annotations


__all__ = ('MyChipsPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.offers import OfferFields
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.my_chips_page_parser import MyChipsPageParsingOptions


@dataclass
class MyChipsPage(FunPayPage):
    """Represents personal chips page (`/chips/<subcategory_id>/trade`)."""

    category_id: int | None
    """Category ID (hidden input `name="game"`)."""

    subcategory_id: int
    """Subcategory ID."""

    fields: OfferFields
    """All form fields for chips offers (editable values)."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: MyChipsPageParsingOptions | None = None
    ) -> MyChipsPage:
        from funpayparsers.parsers.page_parsers.my_chips_page_parser import (
            MyChipsPageParser,
            MyChipsPageParsingOptions,
        )

        options = options or MyChipsPageParsingOptions()
        return MyChipsPageParser(raw_source=raw_source, options=options).parse()
