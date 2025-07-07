__all__ = ('AchievementParserOptions', 'AchievementParser')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.types.common import Achievement


@dataclass(frozen=True)
class AchievementParserOptions(FunPayObjectParserOptions):
    ...


class AchievementParser(FunPayHTMLObjectParser[Achievement, AchievementParserOptions]):
    """
    Class for parsing user achievements.
    Possible locations:
        - On sellers pages (https://funpay.com/<userid>/).
    """

    def _parse(self):
        div = self.tree.css_first('div.achievement-item')
        return Achievement(
            raw_source=div.html,
            css_class=div.css_first('i').attributes['class'],
            text=div.text(deep=False).strip()
        )
