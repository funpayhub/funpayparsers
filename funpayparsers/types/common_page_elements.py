__all__ = ('WebPushStructure', 'AppDataStructure', 'WebPush', 'AppData')

from typing import Literal
from dataclasses import dataclass
from .base import FunPayObject, FunPayObjectStructure


class WebPushStructure(FunPayObjectStructure):
    """
    The structure of the dict representation of a `WebPush` object.
    """
    app: str
    enabled: bool
    hwid_required: bool


class AppDataStructure(FunPayObjectStructure):
    """
    The structure of the dict representation of an `AppData` object.
    """
    locale: Literal['en', 'ru', 'uk']
    csrf_token: str
    user_id: int
    webpush: WebPushStructure


@dataclass
class WebPush(FunPayObject[WebPushStructure]):
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
class AppData(FunPayObject[AppDataStructure]):
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
