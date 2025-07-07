__all__ = ('UserPreviewParser', 'UserPreviewParsingOptions', 'UserPreviewParsingMode')


from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.types.common import UserPreview
from funpayparsers.parsers.utils import extract_css_url

from dataclasses import dataclass
from enum import Enum


class UserPreviewParsingMode(Enum):
    FROM_ORDER_PREVIEW = 0
    FROM_CHAT = 1


@dataclass(frozen=True)
class UserPreviewParsingOptions(ParsingOptions):
    parsing_mode: UserPreviewParsingMode = UserPreviewParsingMode.FROM_ORDER_PREVIEW


class UserPreviewParser(FunPayHTMLObjectParser[UserPreview, UserPreviewParsingOptions]):
    """
    Class for parsing user previews.
    Possible locations:
        - In private chat header (https://funpay.com/en/chat/?node=<chat_id>)
        - On sales page (https://funpay.com/en/orders/trade)
        - On purchases page (https://funpay.com/en/orders/)
    """

    def _parse(self):
        if self.options.parsing_mode is UserPreviewParsingMode.FROM_ORDER_PREVIEW:
            return self._parse_from_order_preview()
        else:
            return self._parse_from_chat()



    def _parse_from_order_preview(self) -> UserPreview:
        user_div = self.tree.css('div.media-user')[0]
        photo_style = user_div.css('div.avatar-photo')[0].attributes['style']
        username_tag = user_div.css('div.media-user-name > span')[0]
        user_status_text: str = user_div.css('div.media-user-status')[0].text().strip()

        return UserPreview(
            raw_source=user_div.html,
            id=int(username_tag.attributes['data-href'].split('/')[-2]),
            username=username_tag.text(strip=True),
            online='online' in user_div.attributes['class'],
            avatar_url=extract_css_url(photo_style),
            banned='banned' in user_div.attributes['class'],
            status_text=user_status_text
        )

    def _parse_from_chat(self) -> UserPreview:
        user_div = self.tree.css('div.media-user')[0]
        username_tag = user_div.css_first('div.media-user-name > a')

        return UserPreview(
            raw_source=user_div.html,
            id=int(username_tag.attributes['href'].split('/')[-2]),
            username=username_tag.text(strip=True),
            online='online' in user_div.attributes['class'],
            avatar_url=user_div.css_first('img.img-circle').attributes['src'],
            banned='banned' in user_div.attributes['class'],
            status_text=user_div.css_first('div.media-user-status').text().strip()
        )
