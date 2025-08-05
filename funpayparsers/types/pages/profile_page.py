from __future__ import annotations


__all__ = ('ProfilePage',)


from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.chat import Chat
from funpayparsers.types.enums import SubcategoryType
from funpayparsers.types.common import UserBadge, UserRating, Achievement
from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.reviews import ReviewsBatch
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.profile_page_parser import ProfilePageParsingOptions


@dataclass
class ProfilePage(FunPayPage):
    """Represents a user profile page (`https://funpay.com/users/<user_id>`)."""

    user_id: int
    """User id."""

    username: str
    """Username."""

    badge: UserBadge | None
    """User badge."""

    achievements: list[Achievement]
    """User achievements."""

    avatar_url: str
    """User avatar url."""

    online: bool
    """Whether the user is online or not."""

    banned: bool
    """Whether the user is banned or not."""

    registration_date_text: str
    """User registration date text."""

    status_text: str | None
    """User status text."""

    rating: UserRating | None
    """User rating."""

    offers: dict[SubcategoryType, dict[int, list[OfferPreview]]] | None
    """User offers."""

    chat: Chat | None
    """Chat with user."""

    reviews: ReviewsBatch | None
    """User reviews."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: ProfilePageParsingOptions | None = None
    ) -> ProfilePage:
        from funpayparsers.parsers.page_parsers.profile_page_parser import (
            ProfilePageParser,
            ProfilePageParsingOptions,
        )

        options = options or ProfilePageParsingOptions()
        return ProfilePageParser(raw_source=raw_source, options=options).parse()
