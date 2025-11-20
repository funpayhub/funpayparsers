from __future__ import annotations


__all__ = ('PrivateChatPreview', 'Chat', 'PrivateChatInfo')

from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject


if TYPE_CHECKING:
    from funpayparsers.types.common import UserPreview, CurrentlyViewingOfferInfo
    from funpayparsers.types.messages import Message


@dataclass
class PrivateChatPreview(FunPayObject):
    """Represents a private chat preview."""

    id: int
    """Chat ID."""

    is_unread: bool
    """True, if chat is unread (orange chat)."""

    username: str
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
    Time of the last message. 
    
    Formats:
        - ``HH:MM`` if the message was sent today.
        - ``'Yesterday'`` (depends on the page language) if the message 
        was sent yesterday.
        
        - ``DD.MM`` if the message was sent the day before yesterday or earlier.
    """


@dataclass
class Chat(FunPayObject):
    """Represents a chat."""

    id: int | None
    """
    Chat ID.
    
    Will be ``None`` if parsing anonymous request response.
    """

    name: str | None
    """
    Chat name.

    Will be ``None`` if parsing anonymous request response.
    """

    interlocutor: UserPreview | None
    """Interlocutor preview. Available in private chats only."""

    is_notifications_enabled: bool | None
    """Whether notifications are enabled or not. Available in private chats only."""

    is_blocked: bool | None
    """Whether notifications are enabled or not. Available in private chats only."""

    history: list[Message]
    """
    Messages history.
    
    - Private chats: last 50 messages.
    - Public chats: last 25 messages.
    """


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
    
    .. warning::
        Not ``None`` only if interlocutors language is english.
    """

    currently_viewing_offer: CurrentlyViewingOfferInfo | None
    """
    Info about the offer currently being viewed by the interlocutor.
    """

    @property
    def registration_timestamp(self) -> int:
        """
        Interlocutors registration timestamp.

        ``0``, if an error occurred while parsing.
        """
        from funpayparsers.parsers.utils import parse_date_string

        try:
            return parse_date_string(self.registration_date_text)
        except ValueError:
            return 0
