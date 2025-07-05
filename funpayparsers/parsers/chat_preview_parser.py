__all__ = ('PrivateChatPreviewParser', 'PrivateChatPreviewParserOptions')

from dataclasses import dataclass

from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.types.chat import PrivateChatPreview


@dataclass(frozen=True)
class PrivateChatPreviewParserOptions(FunPayObjectParserOptions):
    ...


class PrivateChatPreviewParser(
    FunPayHTMLObjectParser[list[PrivateChatPreview], PrivateChatPreviewParserOptions,]):
    """
    Class for parsing private chat previews.
    Possible locations:
        - On private chats page (https://funpay.com/chat/)
    """

    def _parse(self):
        previews = []
        for chat in self.tree.css('a.contact-item'):
            avatar_css = chat.css('div.avatar-photo')[0].attributes['style']

            preview = PrivateChatPreview(
                raw_source=chat.html,
                id=int(chat.attributes['data-id']),
                is_unread='unread' in chat.attributes['class'],
                username=chat.css('div.media-user-name')[0].text(strip=True),
                avatar_url=extract_css_url(avatar_css),
                last_message_id=int(chat.attributes['data-node-msg']),
                last_read_message_id=int(chat.attributes['data-user-msg']),
                last_message_preview=chat.css('div.contact-item-message')[0].text(),
                last_message_time_text=chat.css('div.contact-item-time')[0].text(strip=True),
            )
            previews.append(preview)
        return previews
