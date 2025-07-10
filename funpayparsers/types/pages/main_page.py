from __future__ import annotations


__all__ = ('MainPage', )

from dataclasses import dataclass

from funpayparsers.types.chat import Chat
from funpayparsers.types.categories import Category
from funpayparsers.types.pages.base import FunPayPage


@dataclass
class MainPage(FunPayPage):
    """
    Represents the main page (https://funpay.com).
    """
    last_categories: list[Category]
    """Last opened categories."""

    categories: list[Category]
    """List of categories."""

    secret_chat: Chat | None
    """
    Secret chat (ID: 2, name: 'flood').
    Does not exist on EN version of the main page.
    """
