from __future__ import annotations


__all__ = ('SettingsPage',)


from dataclasses import dataclass

from funpayparsers.types.settings import Settings
from funpayparsers.types.pages.base import FunPayPage


@dataclass
class SettingsPage(FunPayPage):
    """Represents user settings page (``https://funpay.com/account/settings``)."""

    settings: Settings
    """User settings."""

    @classmethod
    def from_raw_source(cls, raw_source: str, options: None = None) -> SettingsPage: ...
