__all__ = ('MainPage', )

from dataclasses import dataclass
from funpayparsers.types.base import FunPayObject
from funpayparsers.types.categories import Category
from funpayparsers.types.chat import Chat
from funpayparsers.types.common_page_elements import PageHeader, AppData


@dataclass
class MainPage(FunPayObject):
    """
    Represents FunPay main page (https://funpay.com)
    """

    header: PageHeader
    """Page header."""

    categories: list[Category]
    """List of categories."""

    secret_chat: Chat
    """Secret chat (ID: 2, name: 'flood')."""

    AppData: AppData
    """AppData."""
