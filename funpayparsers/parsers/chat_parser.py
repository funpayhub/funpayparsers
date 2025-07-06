__all__ = ('ChatParserOptions', 'ChatParser')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.user_preview_parser import UserPreviewParser, UserPreviewParserOptions, UserPreviewParsingMode
from funpayparsers.parsers.messages_parser import MessagesParser, MessagesParserOptions
from funpayparsers.types.chat import Chat
from funpayparsers.types.common import UserPreview
from selectolax.lexbor import LexborNode


@dataclass(frozen=True)
class ChatParserOptions(FunPayObjectParserOptions):
    user_preview_parser_options: UserPreviewParserOptions = UserPreviewParserOptions(parsing_mode=UserPreviewParsingMode.FROM_CHAT)
    messages_parser_options: MessagesParserOptions = MessagesParserOptions()


class ChatParser(FunPayHTMLObjectParser[Chat, ChatParserOptions]):
    """
    Class for parsing chats.
    Possible locations:
        - On main page (https://funpay.com/)
        - On private chat page (https://funpay.com/chat/?node=<chat_id>).
        - On sellers page (https://funpay.com/users/<user_id>/)
        - On some subcategory offers list pages (https://funpay.com/<lots/chips>/<subcategory_id>/
    """

    def _parse(self):
        chat_div = self.tree.css('div.chat')[0]
        interlocutor, notifications, banned = self._parse_chat_header(chat_div)

        messages_div = chat_div.css('div.chat-message-list')[0]
        history = MessagesParser(raw_source=messages_div.html,
                                 options=self.options.messages_parser_options & self.options).parse()

        return Chat(
            raw_source=chat_div.html,
            id=int(chat_div.attributes['data-id']) if chat_div.attributes.get('data-id') else None,
            name=chat_div.attributes['data-name'],
            interlocutor=interlocutor,
            is_notifications_enabled=notifications,
            is_blocked=banned,
            history=history
        )


    def _parse_chat_header(self, div: LexborNode) -> tuple[UserPreview | None, bool | None, bool | None]:
        header_div = div.css('div.chat-header')[0]
        interlocutor_div = header_div.css('div.media-user')

        if not interlocutor_div:
            return None, None, None

        interlocutor = UserPreviewParser(raw_source=interlocutor_div[0].html,
                                         options=self.options.user_preview_parser_options & self.options).parse()

        btn_div = header_div.css('button')
        if not btn_div:
            return interlocutor, None, None
        btn_div = btn_div[0]

        notifications, banned = False, False
        if 'btn-success' in btn_div.attributes['class']:
            notifications, banned = True, False
        elif 'btn-danger' in btn_div.attributes['class']:
            notifications, banned = False, True

        return interlocutor, notifications, banned