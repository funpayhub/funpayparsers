from dataclasses import dataclass

from lxml import html

from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.types.chat import PrivateChatPreview


@dataclass(frozen=True)
class PrivateChatPreviewParserOptions(FunPayObjectParserOptions):
    ...


class PrivateChatPreviewParser(
    FunPayObjectParser[
        list[PrivateChatPreview],
        PrivateChatPreviewParserOptions,
    ]):
    """
    Private chat previews parser.
    TODO: more informative doc-string.
    """

    options_class = PrivateChatPreviewParserOptions

    def _parse(self):
        previews = []
        for p in self.tree.xpath('//a[@class="contact-item"]'):
            source = html.tostring(p, encoding='unicode')
            avatar_css = p.xpath('string(.//div[@class="avatar-photo"][1]/@style)')

            preview = PrivateChatPreview(
                raw_source=source,
                id=int(p.get('data-id')),
                is_unread='unread' in p.get('class'),
                name=p.xpath('string(.//div[@class="media-user-name"][1])'),
                avatar_url=extract_css_url(avatar_css),
                last_message_id=int(p.get('data-node-msg')),
                last_read_message_id=int(p.get('data-user-msg')),
                last_message_preview=p.xpath(
                    'string(.//div[@class="contact-item-message"][1])'),
                last_message_time_text=p.xpath(
                    'string(.//div[@class="contact-item-time"][1])'),
            )
            previews.append(preview)
        return previews
