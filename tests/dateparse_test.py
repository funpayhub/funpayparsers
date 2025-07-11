from __future__ import annotations

from datetime import datetime, timedelta

from funpayparsers.parsers.utils import (
    MONTHS,
    TODAY_WORDS,
    YESTERDAY_WORDS,
    parse_date_string,
)


CURR_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


time_str = "12:20:24"
short_date_str = "12.05.24"
today_date_strs = [f'{word}, 12:20' for word in TODAY_WORDS]
yesterday_date_strs = [f'{word}, 12:20' for word in YESTERDAY_WORDS]
current_year_date_strs = [f'12 {month}, 12:20' for month in MONTHS.keys()]
full_date_strs = [f'12 {month} 2024, 12:20' for month in MONTHS.keys()]

time_obj = CURR_DATE.replace(hour=12, minute=20, second=24)
short_date_obj = datetime(day=12, month=5, year=2024, hour=0, minute=0, second=0, microsecond=0)
today_date_obj = CURR_DATE.replace(hour=12, minute=20)
yesterday_date_obj = CURR_DATE.replace(hour=12, minute=20) - timedelta(days=1)
current_year_date_objs = [datetime(year=CURR_DATE.year, month=i, day=12, hour=12, minute=20, second=0, microsecond=0)
                          for i in MONTHS.values()]
full_date_objs = [datetime(year=2024, month=i, day=12, hour=12, minute=20, second=0, microsecond=0)
                          for i in MONTHS.values()]


def test_time_str_parsing():
    result = parse_date_string(time_str)
    assert datetime.fromtimestamp(result) == time_obj


def test_short_date_str_parsing():
    result = parse_date_string(short_date_str)
    assert datetime.fromtimestamp(result) == short_date_obj


def test_today_date_str_parsing():
    for i in today_date_strs:
        result = parse_date_string(i)
        assert datetime.fromtimestamp(result) == today_date_obj


def test_yesterday_date_str_parsing():
    for i in yesterday_date_strs:
        result = parse_date_string(i)
        assert datetime.fromtimestamp(result) == yesterday_date_obj


def test_current_year_date_str_parsing():
    for i in zip(current_year_date_strs, current_year_date_objs):
        result = parse_date_string(i[0])
        assert datetime.fromtimestamp(result) == i[1]


def test_full_date_str_parsing():
    for i in zip(full_date_strs, full_date_objs):
        result = parse_date_string(i[0])
        assert datetime.fromtimestamp(result) == i[1]