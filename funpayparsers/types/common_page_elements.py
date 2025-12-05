from __future__ import annotations


__all__ = ('AppData', 'WebPush', 'PageHeader')

from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import Currency, Language
from funpayparsers.types.common import MoneyValue


@dataclass
class WebPush(FunPayObject):
    """Represents a WebPush data extracted from an AppData dict."""

    app: str
    """App ID."""

    enabled: bool
    """Is WebPush enabled?"""

    hwid_required: bool
    """Whether HWID is required or not."""


@dataclass
class AppData(FunPayObject):
    """
    Represents an AppData dict.
    """

    locale: Language
    """Current users locale."""

    csrf_token: str
    """CSRF token."""

    user_id: int | None
    """Users ID."""

    webpush: WebPush | None
    """WebPush info."""


@dataclass
class PageHeader(FunPayObject):
    """
    Represents the header section of a FunPay page.

    All fields in this dataclass will be ``None`` if the response is parsed
    from a request made without authentication cookies (i.e., as an anonymous user).
    """

    user_id: int | None
    """Current user ID."""

    username: str | None
    """Current username."""

    avatar_url: str | None
    """Current user avatar URL."""

    language: Language
    """Current language."""

    currency: Currency
    """Current currency."""

    purchases: int | None
    """Number of opened purchases."""

    sales: int | None
    """Number of opened sales."""

    chats: int | None
    """Number of unread chats."""

    balance: MoneyValue | None
    """Current user balance."""

    sales_available: bool
    """Whether sales available or not."""

    logout_token: str | None
    """Logout token (available only for authorized users)."""
