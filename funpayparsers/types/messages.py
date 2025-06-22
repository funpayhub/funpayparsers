__all__ = ('Message',)

from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import UserBadge


@dataclass
class Message(FunPayObject):
    """
    Represents a message from any FunPay chat (private or public).
    """

    id: int
    """Unique message ID."""

    is_heading: bool
    """
    Indicates whether this is a heading message.

    Heading messages contain sender information (ID, username, etc.).
    If this is not a heading message, it means the message was sent by the same user
    as the previous one. The parser does not resolve sender data for such messages
    and sets all related fields to None.
    """

    sender_id: int | None
    """
    Sender ID.

    Will be None by default if the message is not a heading message and 
    `funpayparsers.parsers.utils.resolve_messages_senders` wasn't used.
    """

    sender_username: str | None
    """
    Sender username.

    Will be None by default if the message is not heading and 
    `funpayparsers.parsers.utils.resolve_messages_senders` wasn't used.
    """

    badge: UserBadge | None
    """
    Sender's badge.

    Will be None by default if the message is not heading and 
    `funpayparsers.parsers.utils.resolve_messages_senders` wasn't used.
    """

    send_date_text: str | None
    """
    Message date (as human-readable text).
    Will be None by default if the message is not heading and 
    `funpayparsers.parsers.utils.resolve_messages_senders` wasn't used.
    """

    text: str | None
    """
    Text content of the message.

    Mutually exclusive with `image_url`: a message can contain either text or an image, 
        but not both.
    Will be None if the message contains an image.
    """

    image_url: str | None
    """
    URL of the image in the message.

    Mutually exclusive with `text`: a message can contain either an image or text, 
        but not both.
    Will be None if the message contains text.
    """

    def __str__(self):
        return (f"<Message {self.id} from {self.sender_username} "
                f"[{self.badge.text if self.badge is not None else 'NoBadge'}] "
                f"({self.sender_id}) dated {self.send_date_text}: "
                f"{self.text if self.text is not None else self.image_url}>")


@dataclass
class MessagesChain(FunPayObject):  # todo: add docs
    messages: list[Message]
    previous_message_id: int | None
