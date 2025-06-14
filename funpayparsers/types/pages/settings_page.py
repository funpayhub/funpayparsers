__all__ = ('SettingsPage',)

from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject


@dataclass
class SettingsPage(FunPayObject):
    """
    Represents the settings page.

    https://funpay.com/account/settings
    """

    show_offers: bool
    """Are ALL offers hidden from the table BUT NOT hidden from the profile?"""

    email_notifications: bool
    """Email notifications enabled"""

    push_notifications: bool
    """Push notifications enabled"""

    telegram_notifications: bool
    """Telegram notifications enabled"""

    telegram_username: str | None = None
    """If telegram_notifications is true = parsed telegram first/last name here"""
