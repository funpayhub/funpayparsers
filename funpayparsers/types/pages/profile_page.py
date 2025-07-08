__all__ = ('ProfilePage', )


from dataclasses import dataclass
from funpayparsers.types.pages.base import FunPayPage
from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.reviews import ReviewsBatch
from funpayparsers.types.chat import Chat
from funpayparsers.types.common import UserRating, UserBadge, Achievement
from funpayparsers.types.enums import SubcategoryType
from typing import Literal


@dataclass
class ProfilePage(FunPayPage):
    """
    Represents a user profile page (`https://funpay.com/users/<user_id>`).
    """

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

    status_text: str
    """User status text."""

    rating: UserRating | None
    """User rating."""

    offers: dict[Literal[SubcategoryType.COMMON, SubcategoryType.CURRENCY, SubcategoryType.UNKNOWN], dict[int, list[OfferPreview]]] | None
    """User offers."""

    chat: Chat | None
    """Chat with user."""

    reviews: ReviewsBatch | None
    """User reviews."""
