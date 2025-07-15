from __future__ import annotations


__all__ = ('UserBadgeParser', 'UserBadgeParsingOptions')


from typing import cast
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

    def _parse(self) -> UserBadge:
        badge_span = self.tree.css('span.label')[0]
        return UserBadge(
            raw_source=badge_span.html or '',
            text=badge_span.text(strip=True),
            css_class=cast(str, badge_span.attributes['class']),  # badge_span always has a class
        )
