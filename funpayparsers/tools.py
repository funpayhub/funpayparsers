import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timedelta, timezone

from funpayparsers.types.message import Message

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

TODAY_WORDS = ['сегодня', 'сьогодні', 'today']
YESTERDAY_WORDS = ['вчера', 'вчора', 'yesterday']

DAY_NUM_RE = r'(?:[1-9]|[12][0-9]|3[01])'  # zero-stripped day number (1-31)
HOUR_NUM_RE = r'(?:[0-9]|1[0-9]|2[0-3])'  # zero-stripped hour number (0-23)
MIN_NUM_RE = r'(?:[0-5][0-9])'  # zero-padded minute number (00-59)

TODAY_OR_YESTERDAY_RE = re.compile(
    rf'^({"|".join(TODAY_WORDS + YESTERDAY_WORDS)}), ({HOUR_NUM_RE}):({MIN_NUM_RE})',
)
CURR_YEAR_DATE_RE = re.compile(
    rf'^({DAY_NUM_RE}) ([a-zA-Zа-яА-Я]+), ({HOUR_NUM_RE}):({MIN_NUM_RE})',
)
DATE_RE = re.compile(
    rf'^({DAY_NUM_RE}) ({"|".join(MONTHS.keys())}) (20[0-2][0-9]), ({HOUR_NUM_RE}):({MIN_NUM_RE})',
)


def parse_date_string(date_string: str, /) -> int:
    """
    Parse date string.

    >>> parse_date_string('10 сентября 2022, 13:34')
    1662816840
    """
    date_string = date_string.lower().strip()

    date = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)

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

    raise ValueError(f'Unable to parse date string: {date_string}.')

