__all__ = ('MainPage', )

from dataclasses import dataclass
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.categories import Category
from funpayparsers.types.chat import Chat


@dataclass
class MainPage(FunPayPage):
    """
    Represents the main page (https://funpay.com).
    """
    last_categories: list[Category]
    """Last opened categories."""

    categories: list[Category]
    """List of categories."""

    secret_chat: Chat
    """Secret chat (ID: 2, name: 'flood')."""
