from __future__ import annotations


__all__ = ('AchievementParsingOptions', 'AchievementParser')

from typing import cast
from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import Achievement


@dataclass(frozen=True)
class AchievementParsingOptions(ParsingOptions):
    """Options class for ``AchievementParser``."""

    ...


class AchievementParser(FunPayHTMLObjectParser[Achievement, AchievementParsingOptions]):
    """
    Class for parsing user achievements.

    Possible locations:
        - User profile pages (`https://funpay.com/<userid>/`).
    """

    def _parse(self) -> Achievement:
        div = self.tree.css_first('div.achievement-item')
        return Achievement(
            raw_source=div.html or '',
            # achievement-item always has a class
            css_class=cast(str, div.css_first('i').attributes['class']),
            text=div.text(deep=False).strip(),
        )
