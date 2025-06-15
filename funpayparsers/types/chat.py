from funpayparsers.types.base import FunPayObject
from dataclasses import dataclass


@dataclass
class PrivateChatPreview(FunPayObject):
    """
    Represents a private chat preview.
    """

    id: int
    """Chat ID."""

    is_unread: bool
    """True, if chat is unread (orange chat)."""

    name: str
    """Interlocutor username (chat name)."""

    avatar_url: str
    """Interlocutor avatar URL."""

    last_message_id: int
    """Last message ID."""

    last_read_message_id: int
    """ID of the last message read by the current user."""

    last_message_preview: str
    """
    Preview of the last message (max 250 characters).  
    Excess text (after 250th character) is truncated.  
    Images are displayed as a text message with "Image" text (varies by page language) 
        and do not include a link.
    """

    last_message_time_text: str
    """
    Time of the last message. Formats:
    - `HH:MM` if the message was sent today.
    - `Yesterday` (depends on the page language) if the message was sent yesterday.
    - `DD.MM` if the message was sent the day before yesterday or earlier.
    """
