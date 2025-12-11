from __future__ import annotations


__all__ = ('MyLotsPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.my_lots_page_parser import MyLotsPageParsingOptions


@dataclass
class MyLotsPage(FunPayPage):
    """Represents personal lots page (`/lots/<subcategory_id>/trade`)."""

    subcategory_id: int
    """Subcategory ID of the lots."""

    game_id: int | None
    """Game ID (from raise button data-game, if present)."""

    offers: dict[int | str, OfferPreview]
    """Owned offers mapped by offer ID."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: MyLotsPageParsingOptions | None = None
    ) -> MyLotsPage:
        from funpayparsers.parsers.page_parsers.my_lots_page_parser import (
            MyLotsPageParser,
            MyLotsPageParsingOptions,
        )

        options = options or MyLotsPageParsingOptions()
        return MyLotsPageParser(raw_source=raw_source, options=options).parse()
