from __future__ import annotations


__all__ = ('Message',)

from dataclasses import field, dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import MessageType
from funpayparsers.types.common import UserBadge


@dataclass
class Message(FunPayObject):
    """Represents a message from any FunPay chat (private or public)."""

    id: int
    """Unique message ID."""

    is_heading: bool
    """
    Indicates whether this is a heading message.

    Heading messages contain sender information (ID, username, etc.).
    If this is not a heading message, it means the message was sent by the same user
    as the previous one. The parser does not resolve sender data for such messages
    and sets all related fields to ``None``.
    """

    sender_id: int | None
    """Sender ID."""

    sender_username: str | None
    """Sender username."""

    badge: UserBadge | None
    """Sender's badge."""

    send_date_text: str | None
    """Message date (as human-readable text)."""

    text: str | None
    """
    Text content of the message.

    Mutually exclusive with ``Message.image_url``: 
    a message can contain either text or an image, but not both.

    Will be ``None`` if the message contains an image.
    """

    image_url: str | None
    """
    URL of the image in the message.

    Mutually exclusive with ``Message.text``: 
    a message can contain either an image or text, but not both.
    
    Will be ``None`` if the message contains text.
    """

    chat_id: int | str | None
    """
    Chat ID where the message was sent.

    Parsers obtain this value from the `context` field of the provided options only.

    Context key: ``chat_id``.
    """

    chat_name: str | None
    """
    Chat name where the message was sent.

    This value is available only via the options context during parsing.

    Context key: ``chat_name``.
    """

    _type_cache: tuple[str | None, MessageType] | None = field(
        init=False, repr=False, compare=False, hash=False, default=None
    )

    @property
    def type(self) -> MessageType:
        if self._type_cache is not None:
            if self._type_cache[0] == self.text:
                return self._type_cache[1]

        if not self.text:
            return MessageType.NON_SYSTEM

        if self.sender_id not in [0, 500]:
            return MessageType.NON_SYSTEM

        msg_type = MessageType.get_by_message_text(self.text)
        self._type_cache = (self.text, msg_type)
        return msg_type

    @property
    def timestamp(self) -> int:
        from funpayparsers.parsers.utils import parse_date_string

        if not self.send_date_text:
            return 0

        return parse_date_string(self.send_date_text)
