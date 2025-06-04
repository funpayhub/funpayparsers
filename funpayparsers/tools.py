from collections.abc import Sequence
from .types.message import Message


def parse_date_string(date_string: str) -> int:
    raise NotImplementedError()


def resolve_message_senders(messages: Sequence[Message]):
    raise NotImplementedError()
