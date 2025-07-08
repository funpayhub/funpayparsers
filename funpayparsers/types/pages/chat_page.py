__all__ = ('ChatPage', )

from dataclasses import dataclass
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.chat import PrivateChatPreview, Chat, PrivateChatInfo


@dataclass
class ChatPage(FunPayPage):
    """
    Represents a chat page (`https://funpay.com/chat/?node=<chat_id>`).
    """

    chat_previews: list[PrivateChatPreview] | None
    """List of private chat previews."""

    chat: Chat | None
    """Current opened chat."""

    chat_info: PrivateChatInfo | None
    """Current opened chat info."""
