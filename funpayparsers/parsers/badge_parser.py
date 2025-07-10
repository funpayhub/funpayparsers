from __future__ import annotations


__all__ = ('UserBadgeParser', 'UserBadgeParsingOptions')


from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import UserBadge


@dataclass(frozen=True)
class UserBadgeParsingOptions(ParsingOptions):
    """Options class for ``UserBadgeParser``."""

    ...


class UserBadgeParser(FunPayHTMLObjectParser[UserBadge, UserBadgeParsingOptions]):
    """
    Class for parsing user badges.

    Possible locations:
        - User profile pages (`https://funpay.com/<userid>/`).
        - Chats.
    """

    def _parse(self):
        badge_span = self.tree.css('span.label')[0]
        return UserBadge(
            raw_source=badge_span.html,
            text=badge_span.text(strip=True),
            css_class=badge_span.attributes["class"]
        )
