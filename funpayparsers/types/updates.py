__all__ = ('OrderCounters',
           'ChatBookmarks',
           'ChatCounter',
           'ActionResponse',
           'UpdateObject',
           'Updates')

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.chat import PrivateChatPreview
from funpayparsers.types.messages import Message


UpdateData = TypeVar('UpdateData')


# ------ Simple objects ------
@dataclass
class OrderCounters(FunPayObject):
    """
    Represents an order counters data from updates object.
    """

    purchases: int
    """Active purchases amount."""
    sales: int
    """Active sales amount."""


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

    type: Literal[
        'order_counters', 'chat_counter', 'chat_bookmarks', 'c-p-u', 'chat_node',
    ]
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
    cpu: CurrentlyViewingPage | None
    nodes: dict[int | str, NodeInfo] | None
    unknown_objects: list[dict] | None
    response: ActionResponse | Literal[False]
