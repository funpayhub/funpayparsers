from __future__ import annotations


__all__ = ('PrivateChatPreviewsParser', 'PrivateChatPreviewParsingOptions')

from dataclasses import dataclass

from funpayparsers.types.chat import PrivateChatPreview
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.utils import extract_css_url


@dataclass(frozen=True)
class PrivateChatPreviewParsingOptions(ParsingOptions):
    """Options class for ``PrivateChatPreviewsParser``."""

    ...


class PrivateChatPreviewsParser(
    FunPayHTMLObjectParser[list[PrivateChatPreview], PrivateChatPreviewParsingOptions]
):
    """
    Class for parsing private chat previews.

    Possible locations:
        - Private chats list page (https://funpay.com/chat/)
        - Chats pages (`https://funpay.com/chat/?node=<chat_id>`)
    """

    def _parse(self) -> list[PrivateChatPreview]:
        previews = []
        for chat in self.tree.css('a.contact-item'):
            avatar_css: str = chat.css('div.avatar-photo')[0].attributes['style']  # type: ignore[assignment] # always has a style

            preview = PrivateChatPreview(
                raw_source=chat.html or '',
                id=int(
                    chat.attributes['data-id']  # type: ignore[arg-type] # always has data-id
                ),
                # chat always has a class
                is_unread='unread' in chat.attributes['class'],  # type: ignore[operator]
                username=chat.css('div.media-user-name')[0].text(strip=True),
                avatar_url=extract_css_url(avatar_css),
                last_message_id=int(
                    chat.attributes['data-node-msg']  # type: ignore[arg-type] # always has data-node-msg
                ),
                last_read_message_id=int(
                    chat.attributes['data-user-msg']  # type: ignore[arg-type] # always has data-user-msg
                ),
                last_message_preview=chat.css('div.contact-item-message')[0].text(),
                last_message_time_text=(chat.css('div.contact-item-time')[0].text(strip=True)),
            )
            previews.append(preview)
        return previews
