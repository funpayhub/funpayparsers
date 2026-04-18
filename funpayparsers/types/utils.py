from __future__ import annotations


__all__ = ('parse_money_value_string',)

import re
from typing import Literal, overload

from funpayparsers.types.common import MoneyValue


MONEY_VALUE_RE = re.compile(r'^([+\-]?\d+(?:\.\d+)?)(.+)$')


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
    to_process = money_value_str.strip().replace(' ', '').replace('\u2212', '-')
    if not (match := MONEY_VALUE_RE.fullmatch(to_process)):
        if raise_on_error:
            raise ValueError(f"Unable to parse money value string '{money_value_str}'")
        return None

    value, currency = match.groups()

    return MoneyValue(
        raw_source=raw_source if raw_source is not None else money_value_str,
        value=float(value),
        character=currency,
    )
