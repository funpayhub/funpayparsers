from __future__ import annotations


__all__ = ('SettingsPage',)


from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.settings import Settings
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.settings_page_parser import SettingsPageParsingOptions


@dataclass
class SettingsPage(FunPayPage):
    """Represents the user settings page (``https://funpay.com/account/settings``)."""

    settings: Settings
    """User settings."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: SettingsPageParsingOptions | None = None
    ) -> SettingsPage:
        from funpayparsers.parsers.page_parsers.settings_page_parser import (
            SettingsPageParser,
            SettingsPageParsingOptions,
        )

        options = options or SettingsPageParsingOptions()
        return SettingsPageParser(raw_source=raw_source, options=options).parse()
