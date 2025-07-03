from __future__ import annotations

__all__ = ('PrivateChatPreview', )

from funpayparsers.types.base import FunPayObject
from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from funpayparsers.types.updates import CurrentlyViewingOfferInfo
    from funpayparsers.types import Message


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


@dataclass
class Chat:
    interlocutor: ...
    is_notifications_enabled: bool
    is_blocked: bool
    history: list[Message]


@dataclass
class PrivateChatInfo(FunPayObject):
    """
    Represents a private chat info.
    Located near private chat.
    """

    registration_date_text: str
    """Interlocutors registration date."""

    language: str | None
    """
    Interlocutors language.
    
    Warning:
        Not `None` only if interlocutors language is english.
    """

    currently_viewing_offer: CurrentlyViewingOfferInfo | None
    """
    Info about the offer currently being viewed by the interlocutor.
    """
