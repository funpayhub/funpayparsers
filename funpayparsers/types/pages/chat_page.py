from __future__ import annotations


__all__ = ('ChatPage',)

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.chat import Chat, PrivateChatInfo, PrivateChatPreview
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.chat_page_parser import ChatPageParsingOptions


@dataclass
class ChatPage(FunPayPage):
    """Represents a chat page (`https://funpay.com/chat/?node=<chat_id>`)."""

    chat_previews: list[PrivateChatPreview] | None
    """List of private chat previews."""

    chat: Chat | None
    """Current opened chat."""

    chat_info: PrivateChatInfo | None
    """Current opened chat info."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: ChatPageParsingOptions | None = None
    ) -> ChatPage:
        from funpayparsers.parsers.page_parsers.chat_page_parser import (
            ChatPageParser,
            ChatPageParsingOptions,
        )

        options = options or ChatPageParsingOptions()
        return ChatPageParser(raw_source=raw_source, options=options).parse()
