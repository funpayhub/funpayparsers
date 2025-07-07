__all__ = ('MessagesParsingOptions', 'MessagesParser')

from dataclasses import dataclass
from selectolax.lexbor import LexborNode

from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.types.messages import Message
from funpayparsers.types.common import UserBadge
from funpayparsers.parsers.utils import resolve_messages_senders
from funpayparsers.parsers.badge_parser import UserBadgeParsingOptions, UserBadgeParser


@dataclass(frozen=True)
class MessagesParsingOptions(ParsingOptions):
    """Options class for ``MessagesParser``."""

    sort_by_id: bool = True
    """
    Sorts result messages in ascending order by their ID.
    
    Defaults to ``True``.
    """

    resolve_senders: bool = True
    """
    Determines whether to resolve message senders for non-heading messages.

    In FunPay chats, there are two types of messages: heading and non-heading.
    Heading messages include full information about the sender (ID, username, badge, timestamp, etc.).
    Non-heading messages are sent by the same user as the previous message and do not include sender information.
    
    If ``resolve_senders`` is ``False``, non-heading messages will have sender-related fields set to ``None``.
    
    If ``True``, the ``funpayparsers.parsers.utils.resolve_messages_senders`` function will be used to propagate sender information
    from the preceding heading messages to the subsequent non-heading ones.
    
    Defaults to ``True``.
    """

    user_badge_parsing_options: UserBadgeParsingOptions = UserBadgeParsingOptions()
    """
    Options instance for ``UserBadgeParser``, which is used by ``MessagesParser``.
    
    Defaults to ``UserBadgeParsingOptions()``.
    """


class MessagesParser(FunPayHTMLObjectParser[list[Message], MessagesParsingOptions]):
    """
    Class for parsing messages.
    Possible locations:
        - On chat pages (https://funpay.com/chat/?node=<chat_id>).
        - In runners response.
    """

    def _parse(self):
        messages = []
        for msg_div in self.tree.css('div.chat-msg-item'):
            userid, username, date, badge = None, None, None, None
            has_header = "chat-msg-with-head" in msg_div.attributes["class"]
            if has_header:
                userid, username, date, badge = self._parse_message_header(msg_div)

            if image_tag := msg_div.css('a.chat-img-link'):
                image_url, text = image_tag[0].attributes["href"], None
            else:
                image_url = None

                # Every FunPay *system* message is heading, so we will know sender id
                if userid == 0:
                    text = msg_div.css('div.alert')[0].text().strip()
                else:
                    text = msg_div.css('div.chat-msg-text')[0].text().strip()

            messages.append(Message(
                raw_source=msg_div.html,
                id=int(msg_div.attributes["id"].split("-")[1]),
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

    def _parse_message_header(self, msg_tag: LexborNode) -> tuple[int, str, str, UserBadge | None]:
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

        if user_tag := msg_tag.css('a.chat-msg-author-link'):
            id_, name = int(user_tag[0].attributes["href"].split("/")[-2]), user_tag[0].text(strip=True)

        date = msg_tag.css('div.chat-msg-date')[0].attributes["title"]

        if not (badge := msg_tag.css('span.label')):
            return id_, name, date, None

        return (
            id_,
            name,
            date,
            UserBadgeParser(raw_source=badge[0].html,
                            options=self.options.user_badge_parsing_options).parse()
        )
