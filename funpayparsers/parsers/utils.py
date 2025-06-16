__all__ = ('extract_css_url', 'resolve_messages_senders')

import re
from collections.abc import Iterable
from funpayparsers.types.message import Message
from funpayparsers.types.enums import BadgeType


CSS_URL_RE = re.compile(r'url\(([^()]+)\)', re.IGNORECASE)


def extract_css_url(source: str) -> str:
    """
    Extract the URL from a CSS `url()` pattern in the given string.

    This function looks for the pattern `url(...)`
    and returns the content inside the parentheses.

    Note that it does **not** validate whether the extracted content is a valid URL —
    it simply extracts whatever text is inside `url()`.

    Examples:
        >>> extract_css_url('url(https://sfunpay.com/s/avatar/7q/6b/someimg.jpg)')
        'https://sfunpay.com/s/avatar/7q/6b/someimg.jpg'

        >>> extract_css_url('some text url(not url text)')
        'not url text'

        >>> extract_css_url('not a css url') is None
        True

    :param source: The source string potentially containing a CSS `url()` pattern.
    :return: The extracted text inside `url()` if found; otherwise, `None`.
    """
    match = CSS_URL_RE.search(source)
    return match.group(1) if match else None


def resolve_messages_senders(messages: Iterable[Message], /) -> None:
    """
    Resolves the sender information for non-heading messages by filling in the
    sender_username, sender_id, and badge fields.

    The function respects whether a badge is associated with a user or
    with a specific message. Based on this, it either assigns the badge to
    all subsequent messages from the user or leaves it unset.

    Requires at least one heading message in the sequence.
    Typically, the earliest message in a fetched history is a heading message.
    """
    
    username, userid, badge = None, None, None
    for msg in messages:
        if msg.is_heading:
            username, userid = msg.sender_username, msg.sender_id
            badge = None if msg.badge.type is BadgeType.AUTOISSUE else badge
            continue

        msg.sender_username, msg.sender_id, msg.badge = username, userid, badge
