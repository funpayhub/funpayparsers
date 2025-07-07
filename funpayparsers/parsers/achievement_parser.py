__all__ = ('AchievementParsingOptions', 'AchievementParser')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
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

    def _parse(self):
        div = self.tree.css_first('div.achievement-item')
        return Achievement(
            raw_source=div.html,
            css_class=div.css_first('i').attributes['class'],
            text=div.text(deep=False).strip()
        )
