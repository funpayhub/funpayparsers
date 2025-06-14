__all__ = ('AppData', 'WebPush')

from dataclasses import dataclass
from typing import Literal

from funpayparsers.types.base import FunPayObject


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
class PageHeader(FunPayObject): ...  # todo
