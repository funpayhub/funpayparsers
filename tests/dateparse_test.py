from datetime import datetime, timezone, timedelta
from funpayparsers.parsers.utils import parse_date_string


def test_parse():
    now = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)

    need = [
        # фулл дата (хардкор)
        ("10 сентября 2022, 13:34",
         datetime(2022, 9, 10, 13, 34, tzinfo=timezone.utc)),
        ("1 апреля 2077, 13:37",
         datetime(2077, 4, 1, 13, 37, tzinfo=timezone.utc)),

        # точки (медиум)
        ("01.01.23 00:00",
         datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)),
        ("31.12.22 23:59",
         datetime(2022, 12, 31, 23, 59, tzinfo=timezone.utc)),

        # слэши (медиум)
        ("31/12/22 23:59:59",
         datetime(2022, 12, 31, 23, 59, 59, tzinfo=timezone.utc)),

        # онли время (гига изи)
        ("13:34:00",
         now.replace(hour=13, minute=34, second=0)),
        ("00:00:00",
         now.replace(hour=0, minute=0, second=0)),

        # сегодня / вчера | мб чет еще будет но пока так
        ("сегодня 12:00",
         now.replace(hour=12, minute=0)),
        ("вчера 23:59",
         (now - timedelta(days=1)).replace(hour=23, minute=59)),

        # из заказов
        ("12 января, 12:20",
         now.replace(month=1, day=12, hour=12, minute=20, second=0)),
        ("12 января 2024, 12:20",
         datetime(2024, 1, 12, 12, 20, tzinfo=timezone.utc)),

        # из сообщений обычных + давних
        ("12:20:23",
         now.replace(hour=12, minute=20, second=23)),
        ("12.01.25",
         datetime(2025, 1, 12, 0, 0, 0, tzinfo=timezone.utc)),
    ]

    for date_str, ex in need:
        result_ts = parse_date_string(date_str)
        #print(result_ts)
        ex_ts = int(ex.timestamp())
        delta = abs(result_ts - ex_ts)
        assert delta < 0.05, f"Breaked {date_str}"