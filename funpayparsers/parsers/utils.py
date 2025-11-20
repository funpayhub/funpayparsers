from __future__ import annotations


__all__ = (
    'extract_css_url',
    'resolve_messages_senders',
    'parse_date_string',
    'parse_money_value_string',
    'serialize_form',
)

import re
from typing import Literal, cast, overload
from copy import deepcopy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections.abc import Iterable

from selectolax.lexbor import LexborNode, LexborHTMLParser

from funpayparsers.types.enums import BadgeType
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.messages import Message


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

MONTH_NUM_RE = r'0?\d|1[0-2]'  # month number (1-12 or 01-12)
DAY_RE = r'[01]?\d|2[0-9]|3[01]'  # day number (1-31 or 01-31)
HOUR_RE = r'[01]?\d|2[0-3]'  # hour number (0-23 or 00-23)
MIN_OR_SEC_RE = r'[0-5]?\d'  # minute/second number (0-59 or 00-59)
TIME_RE = rf'(?P<h>{HOUR_RE}):(?P<m>{MIN_OR_SEC_RE})(?::(?P<s>{MIN_OR_SEC_RE}))?'
SEP = r'\s*(,|в|at|о)?\s*'

TIME_ONLY_RE = re.compile(rf'^{TIME_RE}$')
SHORT_DATE_RE = re.compile(rf'^(?P<day>{DAY_RE})\.(?P<month>{MONTH_NUM_RE})\.(?P<year>\d{{2}})$')

TODAY_OR_YESTERDAY_RE = re.compile(rf'^(?P<day>{TODAY_YESTERDAY_RE}){SEP}?\s*{TIME_RE}(?:.*)?$')

DATE_RE = re.compile(
    rf'^(?P<day>{DAY_RE})\s*'
    rf'(?P<month>{MONTHS_NAMES_RE})'
    rf'(?:\s*(?P<year>\d{{4}}))?'
    rf'{SEP}'
    rf'{TIME_RE}'
    rf'(?:.*)?$',
)


def parse_date_string(date_string: str, /) -> int:
    """
    Parses a FunPay-style date string and converts it to a UNIX timestamp.

    Timezone behavior:
    - The input string is expected to represent time in UTC+3 (Europe/Moscow).
    - The returned timestamp is in UTC+0.
    - Internally, the parsed datetime is localized to UTC+3 and then converted to UTC.

    :return: timestamp in UTC+0 timezone.
    """
    date_string = date_string.lower().strip()
    date = datetime.now().replace(second=0, microsecond=0, tzinfo=ZoneInfo('Europe/Moscow'))

    if match := TIME_ONLY_RE.match(date_string):
        return int(
            date.replace(
                hour=int(match.group('h')),
                minute=int(match.group('m')),
                second=int(match.group('s') or 0),
            ).timestamp()
        )

    if match := SHORT_DATE_RE.match(date_string):
        return int(
            date.replace(
                year=int(match.group('year')) + 2000,
                month=int(match.group('month')),
                day=int(match.group('day')),
                hour=0,
                minute=0,
            ).timestamp()
        )

    if match := TODAY_OR_YESTERDAY_RE.match(date_string):
        day = match.group('day')
        date = date.replace(
            hour=int(match.group('h')),
            minute=int(match.group('m')),
        )
        if day in TODAY_WORDS:
            return int(date.timestamp())
        return int((date - timedelta(days=1)).timestamp())

    if match := DATE_RE.match(date_string):
        month = match.group('month')
        month = MONTHS[month]
        return int(
            date.replace(
                year=int(match.group('year') or date.year),
                month=month,
                day=int(match.group('day')),
                hour=int(match.group('h')),
                minute=int(match.group('m')),
                second=int(match.group('s') or 0),
            ).timestamp()
        )

    raise ValueError(f"Unable to parse date string '{date_string}'.")


@overload
def extract_css_url(source: str, /, *, raise_if_not_found: Literal[True] = ...) -> str: ...


@overload
def extract_css_url(source: str, /, *, raise_if_not_found: Literal[False] = ...) -> str | None: ...


def extract_css_url(source: str, /, *, raise_if_not_found: bool = True) -> str | None:
    """
    Extract the URL from a CSS ``'url(*)'`` pattern in the given string.

    This function looks for the pattern ``'url(*)'``
    and returns the content inside the parentheses.

    Note that it does **not** validate whether the extracted content is a valid URL —
    it simply extracts whatever text is inside ``'url()'``.

    Example:
        >>> extract_css_url('url(https://sfunpay.com/s/avatar/7q/6b/someimg.jpg)')
        'https://sfunpay.com/s/avatar/7q/6b/someimg.jpg'

        >>> extract_css_url('some text url(not url text)')
        'not url text'

    :param source: The source string potentially containing a CSS ``'url()'`` pattern.
    :param raise_if_not_found: Raise an exception if the pattern does not contain a URL.
        If ``False``, returns ``None`` insted.

    :return: The extracted text inside ``'url()'`` if found; otherwise, ``None``,
    if ``raise_if_not_found`` = ``False``.
    """
    match = CSS_URL_RE.search(source)
    if match:
        return match.group(1)
    if raise_if_not_found:
        raise LookupError('No suitable URL found.')
    return None


def resolve_messages_senders(messages: Iterable[Message], /) -> None:
    """
    Resolves the sender information for non-heading messages by filling in the
    ``Message.sender_username``, ``Message.sender_id``, and ``Message.badge`` fields.

    The function respects whether a badge is associated with a user or
    with a specific message. Based on this, it either assigns the badge to
    all subsequent messages from the user or leaves it unset.

    Requires at least one heading message in the sequence.
    Typically, the earliest message in a fetched history is a heading message.
    """

    username, userid, badge, send_time = None, None, None, None
    for m in messages:
        if m.is_heading:
            username, userid, send_time = m.sender_username, m.sender_id, m.send_date_text
            badge = (
                deepcopy(m.badge)
                if m.badge and m.badge.type is not BadgeType.AUTO_DELIVERY
                else None
            )
            continue

        m.sender_username, m.sender_id, m.badge, m.send_date_text = (
            username,
            userid,
            badge,
            send_time,
        )


@overload
def parse_money_value_string(
    money_value_str: str, /, *, raw_source: str | None = ..., raise_on_error: Literal[True] = ...
) -> MoneyValue: ...


@overload
def parse_money_value_string(
    money_value_str: str, /, *, raw_source: str | None = ..., raise_on_error: Literal[False] = ...
) -> MoneyValue | None: ...


def parse_money_value_string(
    money_value_str: str,
    /,
    *,
    raw_source: str | None = None,
    raise_on_error: bool = False,
) -> MoneyValue | None:
    """
    Parse money value string.

    Possible formats:
        - `+ 1.23 ₽`
        - `- 1.23 $`
        - `1.23 €`
        - `etc.`

    Whitespaces between sign, value and currency char are allowed.
    String will be stripped before parsing.
    """

    # It is important to replace ' ' with '' to support space seperated values,
    # e.g., 12 345.67
    to_process = money_value_str.strip().replace(' ', '').replace('\u2212', '-')
    if not (match := MONEY_VALUE_RE.fullmatch(to_process)):
        if raise_on_error:
            raise Exception(f"Unable to parse money value string '{money_value_str}'")
        return None

    value, currency = match.groups()

    return MoneyValue(
        raw_source=raw_source if raw_source is not None else money_value_str,
        value=float(value),
        character=currency,
    )


def serialize_form(source: str | LexborNode | LexborHTMLParser) -> dict[str, str]:
    result: dict[str, str] = {}
    if isinstance(source, str):
        if not source:
            return {}
        source = LexborHTMLParser(source)

    forms = source.css('form')
    if not forms:
        return {}
    form = forms[0]

    fields = form.css('*[name]:not([disabled])')
    for field in fields:
        name = field.attributes.get('name') or ''
        value = field.attributes.get('value', '')

        if field.tag == 'textarea':
            value = field.text() or ''

        elif field.tag == 'select':
            selected = field.css('option[selected]')
            value = selected[0].attributes.get('value', '') if selected else ''

        elif field.tag == 'input':
            input_type = cast(str, field.attributes.get('type', '')).lower()
            if input_type == 'checkbox':
                value = 'on' if 'checked' in field.attributes else ''
            elif input_type == 'radio':
                if result.get(name):
                    continue
                value = value if 'checked' in field.attributes else ''

        if value is not None:
            result[name] = value
    return result
