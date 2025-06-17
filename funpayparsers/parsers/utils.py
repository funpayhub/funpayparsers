__all__ = ('extract_css_url', 'resolve_messages_senders', 'parse_date_string')

import re
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone

from funpayparsers.types.enums import BadgeType
from funpayparsers.types.messages import Message

TODAY_WORDS = ['сегодня', 'сьогодні', 'today']
YESTERDAY_WORDS = ['вчера', 'вчора', 'yesterday']

MONTHS = {
    'января': 1,
    'січня': 1,
    'january': 1,
    'февраля': 2,
    'лютого': 2,
    'february': 2,
    'марта': 3,
    'березня': 3,
    'march': 3,
    'апреля': 4,
    'квітня': 4,
    'april': 4,
    'мая': 5,
    'травня': 5,
    'may': 5,
    'июня': 6,
    'червня': 6,
    'june': 6,
    'июля': 7,
    'липня': 7,
    'july': 7,
    'августа': 8,
    'серпня': 8,
    'august': 8,
    'сентября': 9,
    'вересня': 9,
    'september': 9,
    'октября': 10,
    'жовтня': 10,
    'october': 10,
    'ноября': 11,
    'листопада': 11,
    'november': 11,
    'декабря': 12,
    'грудня': 12,
    'december': 12,
}

CSS_URL_RE = re.compile(r'url\(([^()]+)\)', re.IGNORECASE)

DAY_NUM_RE = r'(?:[1-9]|[12][0-9]|3[01])'  # zero-stripped day number (1-31)
HOUR_NUM_RE = r'(?:[0-9]|1[0-9]|2[0-3])'  # zero-stripped hour number (0-23)
MIN_NUM_RE = r'(?:[0-5][0-9])'  # zero-padded minute number (00-59)

TIME_RE = re.compile(r'^([01]?\d|2[0-3]):([0-5]\d):([0-5]\d)$')
SHORT_DATE_RE = re.compile(r'^(\d{1,2}):(\d{1,2}):(\d{2})$')
DOT_DATE_TIME_RE = re.compile(r'^(\d{1,2})\.(\d{1,2})\.(\d{2,4}) (\d{1,2}):(\d{2})$')
DOT_DATE_RE = re.compile(r'^(\d{1,2})\.(\d{1,2})\.(\d{2,4})$')
SLASH_DATE_TIME_RE = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{2}) (\d{1,2}):(\d{2}):(\d{2})$')

TODAY_OR_YESTERDAY_RE = re.compile(
    rf'^({"|".join(TODAY_WORDS + YESTERDAY_WORDS)}),?\s+({HOUR_NUM_RE}):({MIN_NUM_RE})',
)

CURR_YEAR_DATE_RE = re.compile(
    rf'^({DAY_NUM_RE}) ([a-zA-Zа-яА-Я]+),?\s+({HOUR_NUM_RE}):({MIN_NUM_RE})',
)

DATE_RE = re.compile(
    rf'^({DAY_NUM_RE}) ({"|".join(MONTHS.keys())}) (\d{{4}}), ({HOUR_NUM_RE}):({MIN_NUM_RE})',
)

def parse_date_string(date_string: str, /) -> int:
    """
    Parse date string.

    >>> parse_date_string('10 сентября 2022, 13:34')
    1662816840
    """
    date_string = date_string.lower().strip()
    date = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)

    if match := TIME_RE.match(date_string):
        h, m, s = map(int, match.groups())
        return int(date.replace(hour=h, minute=m, second=s).timestamp())

    if match := SHORT_DATE_RE.match(date_string):
        d, mo, y = map(int, match.groups())
        y += 2000
        return int(datetime(y, mo, d, tzinfo=timezone.utc).timestamp())

    if match := SLASH_DATE_TIME_RE.match(date_string):
        d, mo, y, h, m, s = match.groups()
        y = int(y) + 2000
        return int(datetime(y, int(mo), int(d), int(h), int(m), int(s), tzinfo=timezone.utc).timestamp())

    if match := TODAY_OR_YESTERDAY_RE.match(date_string):
        day, h, m = match.groups()
        if day in TODAY_WORDS:
            return int(date.replace(hour=int(h), minute=int(m)).timestamp())
        return int(
            (date.replace(hour=int(h), minute=int(m)) - timedelta(days=1)).timestamp(),
        )

    if match := CURR_YEAR_DATE_RE.match(date_string):
        day, month, h, m = match.groups()
        year = date.year
        month = MONTHS[month]
        return int(
            date.replace(
                year=int(year), month=month, day=int(day), hour=int(h), minute=int(m),
            ).timestamp(),
        )

    if match := DATE_RE.match(date_string):
        day, month, year, h, m = match.groups()
        month = MONTHS[month]
        return int(
            date.replace(
                year=int(year), month=month, day=int(day), hour=int(h), minute=int(m),
            ).timestamp(),
        )

    if match := DOT_DATE_RE.match(date_string):
        d, mo, y = map(int, match.groups())
        if y < 100:
            y += 2000
        return int(datetime(y, mo, d, 0, 0, 0, tzinfo=timezone.utc).timestamp())

    if match := DOT_DATE_TIME_RE.match(date_string):
        d, mo, y, h, m = map(int, match.groups())
        if y < 100:
            y += 2000
        return int(datetime(y, mo, d, h, m, tzinfo=timezone.utc).timestamp())

    raise ValueError(f'Unable to parse date string: {date_string}.')


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
            badge = badge if msg.badge and msg.badge.type is not BadgeType.AUTOISSUE else None
            continue

        msg.sender_username, msg.sender_id, msg.badge = username, userid, badge
