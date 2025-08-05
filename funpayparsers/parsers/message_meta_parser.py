from __future__ import annotations


__all__ = ('MessageMetaParsingOptions', 'MessageMetaParser')


from dataclasses import dataclass

from funpayparsers.types.enums import MessageType
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.messages import MessageMeta


@dataclass(frozen=True)
class MessageMetaParsingOptions(ParsingOptions):
    """Options class for ``MessageMetaParser``."""

    ...


class MessageMetaParser(FunPayHTMLObjectParser[MessageMeta, MessageMetaParsingOptions]):
    """
    Class for parsing message meta data.
    Possible locations:
        - On chat pages (https://funpay.com/chat/?node=<chat_id>).
        - In runners response.
    """

    def _parse(self) -> MessageMeta:
        parse_mapping = {
            MessageType.NEW_ORDER: self.parse_new_order_message,
            MessageType.ORDER_CLOSED: self.parse_order_closed_message,
            MessageType.ORDER_CLOSED_BY_ADMIN: self.parse_order_closed_by_admin_message,
            MessageType.ORDER_REOPENED: self.parse_order_reopened_message,
            MessageType.ORDER_REFUNDED: self.parse_order_refunded_message,
            MessageType.ORDER_PARTIALLY_REFUNDED: self.parse_order_partially_refunded_message,
            MessageType.NEW_FEEDBACK: self.parse_feedback_message,
            MessageType.FEEDBACK_CHANGED: self.parse_feedback_message,
            MessageType.FEEDBACK_DELETED: self.parse_feedback_message,
            MessageType.NEW_FEEDBACK_REPLY: self.parse_feedback_reply_message,
            MessageType.FEEDBACK_REPLY_CHANGED: self.parse_feedback_reply_message,
            MessageType.FEEDBACK_REPLY_DELETED: self.parse_feedback_reply_message,
        }

        msg_type = MessageType.get_by_message_text(self.tree.text())

        if msg_type not in parse_mapping:
            return MessageMeta(raw_source=self.raw_source, type=msg_type)

        result = parse_mapping[msg_type]()
        result.type = msg_type
        return result

    def parse_new_order_message(self) -> MessageMeta:
        links = self.tree.css('a')
        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[1].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
            order_desc=links[1].next.text()[2:],  # type: ignore[union-attr]
            buyer_id=int(links[0].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            buyer_username=links[0].text(strip=True),
        )

    def parse_order_closed_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[1].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
            buyer_id=int(links[0].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            buyer_username=links[0].text(strip=True),
            seller_id=int(links[2].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            seller_username=links[2].text(strip=True),
        )

    def parse_order_closed_by_admin_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[1].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
            admin_id=int(links[0].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            admin_username=links[0].text(strip=True),
            seller_id=int(links[2].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            seller_username=links[2].text(strip=True),
        )

    def parse_order_reopened_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[0].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
        )

    def parse_order_refunded_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[2].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
            buyer_id=int(links[1].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            buyer_username=links[1].text(strip=True),
            seller_id=int(links[0].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            seller_username=links[0].text(strip=True),
        )

    def parse_order_partially_refunded_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[0].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
        )

    def parse_feedback_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[1].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
            buyer_id=int(links[0].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            buyer_username=links[0].text(strip=True),
        )

    def parse_feedback_reply_message(self) -> MessageMeta:
        links = self.tree.css('a')

        return MessageMeta(
            raw_source=self.raw_source,
            order_id=links[1].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
            seller_id=int(links[0].attributes['href'].split('/')[-2]),  # type: ignore[union-attr]
            seller_username=links[0].text(strip=True),
        )
