from __future__ import annotations


__all__ = ('SrasInfoPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.sras import SrasSectionRestriction
from funpayparsers.types.enums import SubcategoryType
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.sras_info_page_parser import (
        SrasInfoPageParsingOptions,
    )


@dataclass
class SrasInfoPage(FunPayPage):
    """Represents the SRAS info page (`https://funpay.com/sras/info`)."""

    restrictions: dict[SubcategoryType, dict[int, SrasSectionRestriction]]
    """Restrictions grouped by subcategory type and subcategory ID."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: SrasInfoPageParsingOptions | None = None
    ) -> SrasInfoPage:
        from funpayparsers.parsers.page_parsers.sras_info_page_parser import (
            SrasInfoPageParser,
            SrasInfoPageParsingOptions,
        )

        options = options or SrasInfoPageParsingOptions()
        return SrasInfoPageParser(raw_source=raw_source, options=options).parse()
