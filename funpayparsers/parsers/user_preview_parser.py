from __future__ import annotations


__all__ = ('UserPreviewParser', 'UserPreviewParsingOptions', 'UserPreviewParsingMode')


from dataclasses import dataclass
from enum import Enum

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import UserPreview
from funpayparsers.parsers.utils import extract_css_url


class UserPreviewParsingMode(Enum):
    """``UserPreviewParser`` parsing modes enumeration."""

    FROM_ORDER_PREVIEW = 0
    """Raw source is/from an order preview."""

    FROM_CHAT = 1
    """Raw source is/from a chat header."""


@dataclass(frozen=True)
class UserPreviewParsingOptions(ParsingOptions):
    """Options class for ``UserPreviewParser``."""

    parsing_mode: UserPreviewParsingMode = UserPreviewParsingMode.FROM_ORDER_PREVIEW
    """
    ``UserPreviewParser`` parsing mode.

    Defaults to ``UserPreviewParsingMode.FROM_ORDER_PREVIEW``.
    """


class UserPreviewParser(FunPayHTMLObjectParser[UserPreview, UserPreviewParsingOptions]):
    """
    Class for parsing user previews.

    Possible locations:
        - Private chat pages (`https://funpay.com/en/chat/?node=<chat_id>`)
        - Sales page (https://funpay.com/en/orders/trade)
        - Purchases page (https://funpay.com/en/orders/)
    """

    def _parse(self) -> UserPreview:
        if self.options.parsing_mode is UserPreviewParsingMode.FROM_ORDER_PREVIEW:
            return self._parse_from_order_preview()
        return self._parse_from_chat()

    def _parse_from_order_preview(self) -> UserPreview:
        user_div = self.tree.css('div.media-user')[0]
        photo_style: str = user_div.css('div.avatar-photo')[0].attributes['style']  # type: ignore[assignment] # always has a style
        username_tag = user_div.css('div.media-user-name > span')[0]
        user_status_text: str = user_div.css('div.media-user-status')[0].text().strip()

        return UserPreview(
            raw_source=user_div.html or '',
            id=int(username_tag.attributes['data-href'].split('/')[-2]),  # type: ignore[union-attr]
            username=username_tag.text(strip=True),
            # user div always has a class
            online='online' in user_div.attributes['class'],  # type: ignore[operator]
            avatar_url=extract_css_url(photo_style),
            # user div always has a class
            banned='banned' in user_div.attributes['class'],  # type: ignore[operator]
            status_text=user_status_text,
        )

    def _parse_from_chat(self) -> UserPreview:
        user_div = self.tree.css('div.media-user')[0]
        username_tag = user_div.css_first('div.media-user-name > a')

        return UserPreview(
            raw_source=user_div.html or '',
            # username tag always has href
            id=int(username_tag.attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            username=username_tag.text(strip=True),
            # user div always has a class
            online='online' in user_div.attributes['class'],  # type: ignore[operator]
            avatar_url=user_div.css_first('img.img-circle').attributes['src'] or '',
            # user div always has a class
            banned='banned' in user_div.attributes['class'],  # type: ignore[operator]
            status_text=user_div.css_first('div.media-user-status').text().strip(),
        )
