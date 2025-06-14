from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.chat import PrivateChatPreview

UpdateType = TypeVar('UpdateType')


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
    Last unread message ID. (?)
    """
    # todo: check what exactly this field represents.
    # todo: looks like, if u will get several messages in 1 update, message will be a
    # list of int. Check it.

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
    """Last unread message ID."""
    # todo: check what exactly this field represents.
    # todo: looks like, if u will get several messages in 1 update, message will be a
    # list of int. Check it.


@dataclass
class ActionResponse(FunPayObject):
    """
    Represents an action response data from updates object.
    """

    error: str | None
    """Error text, if an error occurred while processing a request."""


@dataclass
class UpdateObject(FunPayObject, Generic[UpdateType]):
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

    data: UpdateType
    """Update data."""


@dataclass
class Updates(FunPayObject):
    """
    Represents an updates object, returned by runner.
    """

    order_counters: UpdateObject[OrderCounters] | None
    chat_counter: UpdateObject[ChatCounter] | None
    chat_bookmarks: UpdateObject[ChatBookmarks] | None
    cpu: None  # todo: implement a class, that represents a c-p-u data.
    objects: list[None]
    response: ActionResponse | Literal[False]


#  todo: NodeObject, NodeMessageObject, ChatNodeData
#  todo: see requesting chat history.
#  todo: docstrings for Updates object.
#  todo: dont inherit from FunPayObject? Too many raw_source fields for nested dc's.
