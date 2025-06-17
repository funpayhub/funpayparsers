__all__ = ('MessagesParserOptions', 'MessagesParser')

from dataclasses import dataclass

from lxml import html

from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.types.messages import Message
from funpayparsers.types.common import UserBadge
from funpayparsers.parsers.utils import resolve_messages_senders
from funpayparsers.parsers.badge_parser import UserBadgeParserOptions, UserBadgeParser


@dataclass(frozen=True)
class MessagesParserOptions(FunPayObjectParserOptions):
    sort_by_id: bool = True
    resolve_senders: bool = True


class MessagesParser(FunPayObjectParser[list[Message], MessagesParserOptions]):
    options_cls = MessagesParserOptions

    def _parse(self):
        messages = []
        for msg_div in self.tree.xpath('//div[contains(@class, "chat-msg-item")]'):
            userid, username, date, badge = None, None, None, None

            message_id = int(msg_div.get("id").split("-")[1])
            has_header, msg_badge = "chat-msg-with-head" in msg_div.get("class"), None

            if has_header:
                userid, username, date, badge = self._parse_message_header(msg_div)

            if image_tag := msg_div.xpath('.//a[@class="chat-img-link"]'):
                image_url, text = image_tag[0].get("href"), None
            else:
                image_url = None

                # Every FunPay message is heading, so we will know sender id
                if userid == 0:
                    text = msg_div.xpath(
                        'string(.//div[contains(@class, "alert")][1])'
                    ).strip()
                else:
                    text = msg_div.xpath('string(.//div[@class="chat-msg-text"][1])')

            messages.append(Message(
                raw_source=html.tostring(msg_div, encoding="unicode"),
                id=message_id,
                is_heading=has_header,
                sender_id=userid,
                sender_username=username,
                send_date_text=date,
                badge=badge,
                text=text,
                image_url=image_url,
            ))

        if self.options.sort_by_id or self.options.resolve_senders:
            messages.sort(key=lambda m: m.id)

        if self.options.resolve_senders:
            resolve_messages_senders(messages)
        return messages

    def _parse_message_header(self, msg_tag: html.HtmlElement) -> tuple[int, str, str, UserBadge | None]:
        """
        Parses the message header to extract the author ID, author nickname,
        and an optional author/message badge.

        :param msg_tag: The HTML element containing the message header.

        :return: A tuple containing:
            - Author ID as an integer.
            - Author nickname as a string.
            - A MessageBadge object if a badge is present, otherwise None.
        """

        id_, name = 0, "FunPay"

        if user_tag := msg_tag.xpath('.//a[@class="chat-msg-author-link"][1]'):
            id_, name = int(user_tag[0].get("href").split("/")[-2]), user_tag[0].text

        date = msg_tag.xpath('.//div[@class="chat-msg-date"]')[0].get("title")

        if not (badge := msg_tag.xpath('.//span[contains(@class, "author-label")]')):
            return id_, name, date, None

        return (
            id_,
            name,
            date,
            UserBadgeParser(html.tostring(badge[0], encoding="unicode"),
                            options=UserBadgeParserOptions() & self.options).parse()
        )
