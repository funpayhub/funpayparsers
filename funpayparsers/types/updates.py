__all__ = ('OrderCounters',
           'ChatBookmarks',
           'ChatCounter',
           'CurrentlyViewingPageHTML',
           'CurrentlyViewingPage',
           'NodeInfo',
           'ChatNode',
           'ActionResponse',
           'UpdateObject',
           'Updates')

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.chat import PrivateChatPreview
from funpayparsers.types.messages import Message
from funpayparsers.types.enums import UpdateType


UpdateData = TypeVar('UpdateData')


# ------ Simple objects ------
@dataclass
class OrderCounters(FunPayObject):
    """
    Represents an order counters data from updates object.
    """

    purchases: int
    """Active purchases amount (`buyer` field)."""
    sales: int
    """Active sales amount (`seller` field)."""


@dataclass
class ChatBookmarks(FunPayObject):
    """
    Represents a chat bookmarks data from updates object.
    """

    counter: int
    """Unread chats amount."""

    message: int
    """
    ID of the latest unread message.
    If there are new messages in multiple chats, this field contains the ID of the most recent message among all of them.
    """

    order: list[int]
    """Order of chat previews (list of chats IDs)."""

    chat_previews: list[PrivateChatPreview]
    """List of chat previews."""


@dataclass
class ChatCounter(FunPayObject):
    """
    Represents a chat counter data from updates object.
    """

    counter: int
    """Unread chats amount."""

    message: int
    """
    ID of the latest unread message.
    If there are new messages in multiple chats, this field contains the ID of the most recent message among all of them.
    """


# ------ C-P-U ------
@dataclass
class CurrentlyViewingPageHTML(FunPayObject):
    desktop: str
    mobile: str


@dataclass
class CurrentlyViewingPage(FunPayObject):
    html: CurrentlyViewingPageHTML


# ------ Nodes ------
@dataclass
class NodeInfo(FunPayObject):
    id: int
    name: str
    silent: bool


@dataclass
class ChatNode(FunPayObject):
    node: NodeInfo
    messages: list[Message]
    has_history: bool


# ------ Response to action ------
@dataclass
class ActionResponse(FunPayObject):
    """
    Represents an action response data from updates object.
    """

    error: str | None
    """Error text, if an error occurred while processing a request."""


@dataclass
class UpdateObject(FunPayObject, Generic[UpdateData]):
    """
    Represents a single update data from updates object.
    """

    type: UpdateType
    """Update type."""

    id: int | str  # todo: wtf is this? tag = id
    """Update ID."""

    tag: str
    """Update tag."""

    data: UpdateData
    """Update data."""


@dataclass
class Updates(FunPayObject):
    """
    Represents an updates object, returned by runner.
    """

    order_counters: UpdateObject[OrderCounters] | None
    chat_counter: UpdateObject[ChatCounter] | None
    chat_bookmarks: UpdateObject[ChatBookmarks] | None
    cpu: UpdateObject[CurrentlyViewingPage] | None
    nodes: dict[int | str, UpdateObject[NodeInfo]] | None
    unknown_objects: list[dict] | None
    response: ActionResponse | None
