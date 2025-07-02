__all__ = ('UserBadgeParser', 'UserBadgeParserOptions')


from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayHTML2ObjectParser
from funpayparsers.types.common import UserBadge
from dataclasses import dataclass


@dataclass(frozen=True)
class UserBadgeParserOptions(FunPayObjectParserOptions):
    ...


class UserBadgeParser(FunPayHTML2ObjectParser[UserBadge, UserBadgeParserOptions]):
    """
    Class for parsing user badges.
    Possible locations:
        - On sellers pages (near username).
        - In chats (near messages).
    """
    def _parse(self):
        badge_span = self.tree.css('span.label')[0]
        return UserBadge(
            raw_source=badge_span.html,
            text=badge_span.text(strip=True),
            css_class=badge_span.attributes["class"]
        )
