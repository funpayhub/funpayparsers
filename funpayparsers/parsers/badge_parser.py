__all__ = ('UserBadgeParser', 'UserBadgeParserOptions')


from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.types.common import UserBadge
from dataclasses import dataclass
from lxml import html


@dataclass(frozen=True)
class UserBadgeParserOptions(FunPayObjectParserOptions):
    ...


class UserBadgeParser(FunPayObjectParser[UserBadge, UserBadgeParserOptions]):
    def _parse(self):
        badge_div = self.tree.xpath('//span[contains(@class, "label")]')[0]
        return UserBadge(
            raw_source=html.tostring(badge_div, encoding="unicode"),
            text=badge_div.text,
            css_class=badge_div.get("class")
        )
