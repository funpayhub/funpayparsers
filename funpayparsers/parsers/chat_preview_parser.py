from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.types.chat import PrivateChatPreview
from lxml import html
from dataclasses import dataclass


@dataclass(frozen=True)
class PrivateChatPreviewParserOptions(FunPayObjectParserOptions):
    sort_by_id: bool = True
    resolve_senders: bool = True


class PrivateChatPreviewParser(
    FunPayObjectParser[list[PrivateChatPreview], PrivateChatPreviewParserOptions]):
    options_class = PrivateChatPreviewParserOptions

    def _parse(self):
        previews = []
        for chat in self.tree.xpath('//a[@class="contact-item"]'):
            source = html.tostring(chat, encoding='unicode')
            avatar_style = chat.xpath('string(.//div[@class="avatar-photo"][1]/@style)')

            preview =  PrivateChatPreview(
                raw_source=source,
                id=int(chat.get('data-id')),
                is_unread='unread' in chat.get('class'),
                interlocutor_username=chat.xpath(
                    'string(.//div[@class="media-user-name"][1])'),
                interlocutor_avatar_url=parse_avatar_link(avatar_style),
                last_message_id=int(chat.get('data-node-msg')),
                last_read_message_id=int(chat.get('data-user-msg')),
                last_message_preview=chat.xpath(
                    'string(.//div[@class="contact-item-message"][1])'),
                last_message_time_text=chat.xpath(
                    'string(.//div[@class="contact-item-time"][1])'),
            )

        return previews

