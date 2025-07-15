from __future__ import annotations


__all__ = ('ChatParsingOptions', 'ChatParser')

from typing import cast
from dataclasses import dataclass

from selectolax.lexbor import LexborNode

from funpayparsers.types.chat import Chat
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import UserPreview
from funpayparsers.parsers.messages_parser import MessagesParser, MessagesParsingOptions
from funpayparsers.parsers.user_preview_parser import (
    UserPreviewParser,
    UserPreviewParsingMode,
    UserPreviewParsingOptions,
)


@dataclass(frozen=True)
class ChatParsingOptions(ParsingOptions):
    """Options class for ``ChatParser``."""

    user_preview_parsing_options: UserPreviewParsingOptions = UserPreviewParsingOptions()
    """
    Options instance for ``UserPreviewParser``, which is used by ``ChatParser``.
    
    ``parsing_mode`` option is hardcoded in ``ChatParser`` and is therefore ignored 
    if provided externally.
    
    Defaults to ``UserPreviewParsingOptions()``.
    """

    messages_parsing_options: MessagesParsingOptions = MessagesParsingOptions()
    """
    Options instance for ``MessagesParser``, which is used by ``ChatParser``.
    
    Defaults to ``MessagesParsingOptions()``.
    """


class ChatParser(FunPayHTMLObjectParser[Chat, ChatParsingOptions]):
    """
    Class for parsing chats.

    Possible locations:
        - Main page (https://funpay.com/)
        - Chat pages (`https://funpay.com/chat/?node=<chat_id>`).
        - User profile pages (`https://funpay.com/users/<user_id>/`)
        - Some subcategory offers list pages
        (`https://funpay.com/<lots/chips>/<subcategory_id>/`)
    """

    def _parse(self) -> Chat:
        chat_div = self.tree.css('div.chat')[0]
        interlocutor, notifications, banned = self._parse_chat_header(chat_div)

        chat_id = (
            int(cast(str, chat_div.attributes['data-id']))
            if chat_div.attributes.get('data-id')
            else None
        )

        chat_name: str = cast(str, chat_div.attributes.get('data-name'))

        messages_div = chat_div.css('div.chat-message-list')[0]
        history = MessagesParser(
            raw_source=messages_div.html or '',
            options=self.options.messages_parsing_options,
            context={'chat_id': chat_id, 'chat_name': chat_name},
        ).parse()

        return Chat(
            raw_source=chat_div.html or '',
            id=chat_id,
            name=chat_name,
            interlocutor=interlocutor,
            is_notifications_enabled=notifications,
            is_blocked=banned,
            history=history,
        )

    def _parse_chat_header(
        self, div: LexborNode
    ) -> tuple[UserPreview | None, bool | None, bool | None]:
        header_div = div.css('div.chat-header')[0]
        interlocutor_divs = header_div.css('div.media-user')

        if not interlocutor_divs:
            return None, None, None

        interlocutor = UserPreviewParser(
            raw_source=cast(str, interlocutor_divs[0].html),
            options=self.options.user_preview_parsing_options,
            parsing_mode=UserPreviewParsingMode.FROM_CHAT,
        ).parse()

        btn_divs = header_div.css('button')
        if not btn_divs:
            return interlocutor, None, None
        btn_div = btn_divs[0]

        notifications, banned = False, False
        if 'btn-success' in btn_div.attributes['class']:  # type: ignore[operator]
            notifications, banned = True, False
        elif 'btn-danger' in btn_div.attributes['class']:  # type: ignore[operator]
            notifications, banned = False, True

        return interlocutor, notifications, banned
