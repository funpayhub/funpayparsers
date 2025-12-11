from __future__ import annotations


__all__ = (
    'OrdersCounters',
    'ChatBookmarks',
    'ChatCounter',
    'NodeInfo',
    'ChatNode',
    'ActionResponse',
    'RunnerResponseObject',
    'RunnerResponse',
)

from typing import Any, Generic, Literal, TypeVar
from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.chat import PrivateChatPreview
from funpayparsers.types.enums import RunnerDataType
from funpayparsers.types.common import CurrentlyViewingOfferInfo
from funpayparsers.types.messages import Message


UpdateData = TypeVar('UpdateData')


# ------ Simple objects ------
@dataclass
class OrdersCounters(FunPayObject):
    """Represents an order counters data from runner response."""

    purchases: int
    """Active purchases amount."""
    sales: int
    """Active sales amount."""


@dataclass
class ChatBookmarks(FunPayObject):
    """Represents a chat bookmarks data from runner response."""

    counter: int
    """Unread chats amount."""

    latest_message_id: int
    """
    ID of the latest unread message.
    
    If there are new messages in multiple chats, 
    this field contains the ID of the most recent message among all of them.
    """

    order: list[int]
    """Order of chat previews (list of chats IDs)."""

    chat_previews: list[PrivateChatPreview]
    """List of chat previews."""


@dataclass
class ChatCounter(FunPayObject):
    """Represents a chat counter data from runner response."""

    counter: int
    """Unread chats amount."""

    latest_message_id: int
    """
    ID of the latest unread message.
    
    If there are new messages in multiple chats, 
    this field contains the ID of the most recent message among all of them.
    """


# ------ Nodes ------
@dataclass
class NodeInfo(FunPayObject):
    """Represents a chat info in chat data from runner response."""

    id: int
    """Chat ID."""

    name: str
    """Chat name."""

    silent: bool
    """Purpose is unknown."""  # todo


@dataclass
class ChatNode(FunPayObject):
    """Represents a chat data from runner response."""

    node: NodeInfo
    """Chat info."""

    messages: list[Message]
    """List of messages."""

    has_history: bool
    """Purpose is unknown."""  # todo


# ------ Response to action ------
@dataclass
class ActionResponse(FunPayObject):
    """Represents an action response data from runner response."""

    error: str | None
    """Error text, if an error occurred while processing a request."""


# ------ Update obj ------
@dataclass
class RunnerResponseObject(FunPayObject, Generic[UpdateData]):
    """Represents a single runner response object from runner response."""

    type: RunnerDataType
    """Object type."""

    id: int | str
    """Related ID (user ID / chat ID / etc)."""

    tag: str
    """Runner tag."""

    data: UpdateData | Literal[False]
    """Runner object data."""


@dataclass
class RunnerResponse(FunPayObject):
    """Represents a runner response."""

    orders_counters: RunnerResponseObject[OrdersCounters] | None
    """Orders counters data."""

    chat_counter: RunnerResponseObject[ChatCounter] | None
    """Chat counter data."""

    chat_bookmarks: RunnerResponseObject[ChatBookmarks] | None
    """Chat bookmarks data."""

    cpu: list[RunnerResponseObject[CurrentlyViewingOfferInfo]] | None
    """Currently viewing offer info."""

    nodes: list[RunnerResponseObject[ChatNode]] | None
    """Nodes data."""

    unknown_objects: list[dict[str, Any]] | None
    """Datas with unknown type."""

    response: ActionResponse | None
    """Action response."""
