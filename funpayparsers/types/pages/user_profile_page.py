__all__ = ('UserProfilePage',)

from dataclasses import dataclass

from funpayparsers.tools import MONTHS
from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import UserBadge


@dataclass
class UserProfilePage(FunPayObject):
    """
    Represents a profile page.
    """

    username: str
    """
    Username of the user.
    Can be changed by admins
    If you need to save user -- use ONLY user_id
    """

    avatar_link: str
    """Url link to view avatar."""

    online: bool
    """Online status."""

    last_online: None  # todo
    """If the user is offline, there will be something related to last online"""

    badge: UserBadge | None
    """User badge (support, не активирован, арбiтраж) / common.UserBadge"""

    achievements: list[str] | None
    """User Achievements (Pioneer, Cosplay Festival Visitor 2024)"""

    reg_date: str  # todo need parse reg_date with MONTHS
    """todo formatted registration date / maybe datetime object"""

    reviews_amount: int | None
    """Total number of reviews"""

    grade: float | int | None
    """Average rating | 4.8 stars / 5 stars"""

    reivews: None  # todo
    """#TODO: Replace with an object to represent the user last 25 reviews."""

    lots: None  # todo
    """#TODO: Replace with a object to represent and manage user lots."""
