__all__ = ('AppData', 'WebPush', 'PageHeader')

from dataclasses import dataclass
from typing import Literal

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.enums import Currency


@dataclass
class WebPush(FunPayObject):
    """
    Represents a WebPush data extracted from an AppData dict.
    """

    app: str
    """App ID."""

    enabled: bool
    """Is WebPush enabled?"""

    hwid_required: bool
    """Does it requires HWID?"""


@dataclass
class AppData(FunPayObject):
    """
    Represents an AppData dict.
    """

    locale: Literal['en', 'ru', 'uk']
    """Current users locale."""

    csrf_token: str
    """CSRF token."""

    user_id: int
    """Users ID."""

    webpush: WebPush
    """WebPush info."""


@dataclass
class PageHeader(FunPayObject):
    """
    Represents the header section of a FunPay page.

    All fields in this dataclass will be `None` if the response is parsed
    from a request made without authentication cookies (i.e., as an anonymous user).
    """
    user_id: int | None
    """Current user ID."""

    username: str | None
    """Current username."""

    avatar_url: str | None
    """Current user avatar URL."""

    language: ...
    """Current language."""

    currency: Currency | None
    """Current currency."""

    purchases: int | None
    """Number of opened purchases."""

    sales: int | None
    """Number of opened sales."""

    chats: int | None
    """Number of unread chats."""

    balance: MoneyValue | None
    """Current user balance."""
