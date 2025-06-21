__all__ = ('extract_css_url', 'resolve_messages_senders', 'parse_date_string', 'parse_money_value_string')

import re
from collections.abc import Iterable
from funpayparsers.types.messages import Message
from datetime import datetime, timedelta
from copy import deepcopy

from funpayparsers.types.enums import BadgeType
from funpayparsers.types.common import MoneyValue


CSS_URL_RE = re.compile(r'url\(([^()]+)\)', re.IGNORECASE)
MONEY_VALUE_RE = re.compile(r'^([+\-]?\d+(?:\.\d+)?)(.)$')


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

MONTHS_NAMES_RE = '|'.join(MONTHS.keys())
TODAY_YESTERDAY_RE = '|'.join(TODAY_WORDS + YESTERDAY_WORDS)

MONTH_NUM_RE = r'0?\d|1[0-2]'  # zero-padded or stripped month number (1-12 or 01-12)
DAY_RE = r'[01]?\d|2[0-9]|3[01]'  # zero-padded or stripped day number (1-31 or 01-31)
HOUR_RE = r'[01]?\d|2[0-3]'  # zero-padded or stripped hour number (0-23 or 00-23)
MIN_OR_SEC_RE = r'[0-5]?\d'  # zero-padded or stripped minute/second number (0-59 or 00-59)

TIME_RE = re.compile(rf'^({HOUR_RE}):({MIN_OR_SEC_RE}):({MIN_OR_SEC_RE})$')
SHORT_DATE_RE = re.compile(rf'^({DAY_RE})\.({MONTH_NUM_RE})\.(\d{{2}})$')

TODAY_OR_YESTERDAY_RE = re.compile(
    rf'^({TODAY_YESTERDAY_RE}),?\s*({HOUR_RE}):({MIN_OR_SEC_RE})$',
)

CURR_YEAR_DATE_RE = re.compile(
    rf'^({DAY_RE})\s*({MONTHS_NAMES_RE}),?\s*({HOUR_RE}):({MIN_OR_SEC_RE})$',
)

DATE_RE = re.compile(
    rf'^({DAY_RE})\s*({MONTHS_NAMES_RE})\s*(\d{{4}}),?\s*({HOUR_RE}):({MIN_OR_SEC_RE})$',
)


def parse_date_string(date_string: str, /) -> int:
    """
    Parse date string.
    """
    date_string = date_string.lower().strip()
    date = datetime.now().replace(second=0, microsecond=0)

    if match := TIME_RE.match(date_string):
        h, m, s = map(int, match.groups())
        return int(date.replace(hour=h, minute=m, second=s).timestamp())

    if match := SHORT_DATE_RE.match(date_string):
        d, mo, y = map(int, match.groups())
        return int(datetime(year=y+2000, month=mo, day=d,
                            hour=0, minute=0, second=0, microsecond=0).timestamp())

    if match := TODAY_OR_YESTERDAY_RE.match(date_string):
        day, h, m = match.groups()
        date = date.replace(hour=int(h), minute=int(m))
        if day in TODAY_WORDS:
            return int(date.timestamp())
        return int((date - timedelta(days=1)).timestamp())

    if match := CURR_YEAR_DATE_RE.match(date_string):
        day, month, h, m = match.groups()
        year = date.year
        month = MONTHS[month]
        return int(date.replace(year=int(year), month=month, day=int(day), hour=int(h), minute=int(m)).timestamp())

    if match := DATE_RE.match(date_string):
        day, month, year, h, m = match.groups()
        month = MONTHS[month]
        return int(date.replace(year=int(year), month=month, day=int(day), hour=int(h), minute=int(m)).timestamp())

    raise ValueError(f'Unable to parse date string \'{date_string}\'.')


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
            badge = deepcopy(msg.badge) if msg.badge and msg.badge.type is not BadgeType.AUTOISSUE else None
            continue

        msg.sender_username, msg.sender_id, msg.badge = username, userid, badge


def parse_money_value_string(money_value_str: str, /, *, raw_source: str | None = None,
                             raise_on_error: bool = False) -> MoneyValue | None:
    """
    Parse money value string.
    Possible formats:
    + 1.23 ₽,
    - 1.23 $,
    1.23 €,
    etc.

    Whitespaces between sign, value and currency char are allowed.
    String will be stripped before parsing.
    """

    to_process = money_value_str.strip().replace(' ', '').replace('\u2212', '-')
    if not (match := MONEY_VALUE_RE.fullmatch(to_process)):
        if raise_on_error:
            raise Exception(f'Unable to parse money value string \'{money_value_str}\'')
        return None

    value, currency = match.groups()

    return MoneyValue(raw_source=raw_source if raw_source is not None else money_value_str,
                      value=float(value), character=currency)
