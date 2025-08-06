from __future__ import annotations


__all__ = ('MainPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.chat import Chat
from funpayparsers.types.categories import Category
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.main_page_parser import MainPageParsingOptions


@dataclass
class MainPage(FunPayPage):
    """Represents the main page (https://funpay.com)."""

    last_categories: list[Category]
    """Last opened categories."""

    categories: list[Category]
    """List of categories."""

    secret_chat: Chat | None
    """
    Secret chat (ID: ``2``, name: ``'flood'``).
    
    Does not exist on EN version of the main page.
    """

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: MainPageParsingOptions | None = None
    ) -> MainPage:
        from funpayparsers.parsers.page_parsers.main_page_parser import (
            MainPageParser,
            MainPageParsingOptions,
        )

        options = options or MainPageParsingOptions()
        return MainPageParser(raw_source=raw_source, options=options).parse()
