from __future__ import annotations


__all__ = ('ProfilePageParsingOptions', 'ProfilePageParser')


from typing import cast
from dataclasses import dataclass

from funpayparsers.types.enums import BadgeType, SubcategoryType
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferPreview
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.parsers.chat_parser import ChatParser, ChatParsingOptions
from funpayparsers.parsers.badge_parser import UserBadgeParser, UserBadgeParsingOptions
from funpayparsers.parsers.rating_parser import (
    UserRatingParser,
    UserRatingParsingOptions,
)
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.reviews_parser import ReviewsParser, ReviewsParsingOptions
from funpayparsers.types.pages.profile_page import ProfilePage
from funpayparsers.parsers.achievement_parser import (
    AchievementParser,
    AchievementParsingOptions,
)
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.parsers.offer_previews_parser import (
    OfferPreviewsParser,
    OfferPreviewsParsingOptions,
)


@dataclass(frozen=True)
class ProfilePageParsingOptions(ParsingOptions):
    """Options class for ``ProfilePageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``ProfilePageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``ProfilePageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    user_rating_parsing_options: UserRatingParsingOptions = UserRatingParsingOptions()
    """
    Options instance for ``UserRatingParser``, which is used by ``ProfilePageParser``.

    Defaults to ``UserRatingParsingOptions()``.
    """

    offer_previews_parsing_options: OfferPreviewsParsingOptions = OfferPreviewsParsingOptions()
    """
    Options instance for ``OfferPreviewsParser``, 
    which is used by ``ProfilePageParser``.

    Defaults to ``OfferPreviewsParsingOptions()``.
    """

    user_badge_parsing_options: UserBadgeParsingOptions = UserBadgeParsingOptions()
    """
    Options instance for ``UserBadgeParser``, which is used by ``ProfilePageParser``.

    Defaults to ``UserBadgeParsingOptions()``.
    """

    chat_parsing_options: ChatParsingOptions = ChatParsingOptions()
    """
    Options instance for ``ChatParser``, which is used by ``ProfilePageParser``.

    Defaults to ``ChatParsingOptions()``.
    """

    reviews_parsing_options: ReviewsParsingOptions = ReviewsParsingOptions()
    """
    Options instance for ``ReviewsParser``, which is used by ``ProfilePageParser``.

    Defaults to ``ReviewsParsingOptions()``.
    """

    achievement_parsing_options: AchievementParsingOptions = AchievementParsingOptions()
    """
    Options instance for ``AchievementParser``, which is used by ``ProfilePageParser``.

    Defaults to ``AchievementParsingOptions()``.
    """


class ProfilePageParser(FunPayHTMLObjectParser[ProfilePage, ProfilePageParsingOptions]):
    """
    Class for parsing user profile pages (`https://funpay.com/users/<user_id>/`).
    """

    def _parse(self) -> ProfilePage:
        profile_header = self.tree.css_first('div.profile-header')
        reg_date_text_div = profile_header.css('div.param-item')
        offer_divs = self.tree.css('div.mb20 div.offer')
        achievements_divs = self.tree.css('div.achievement-item')
        chat_div = self.tree.css('div.chat')

        # It is better to parse the rating from the reviews block,
        # because some old profiles have only old type reviews (without rating)
        # and then there is no full rating block in profile header,
        # but in the reviews block it is always present when there are any reviews.
        rating_div = self.tree.css_first('div.param-item.mb10')
        reviews_div = self.tree.css('div.offer:has(div.dyn-table-body)') if rating_div else None

        badges = []
        for i in profile_header.css('small.user-badges > span'):
            badges.append(
                UserBadgeParser(
                    i.html or '', options=self.options.user_badge_parsing_options
                ).parse(),
            )

        for j in badges:
            if j.type is BadgeType.BANNED:
                banned = True
                badges.remove(j)
                badge = badges[0] if badges else None
                break
        else:
            banned = False
            badge = badges[0] if badges else None

        if offer_divs:
            offers: dict[SubcategoryType, dict[int, list[OfferPreview]]] | None = {
                SubcategoryType.COMMON: {},
                SubcategoryType.CURRENCY: {},
                SubcategoryType.UNKNOWN: {},
            }
            for offer_div in offer_divs:
                url: str = offer_div.css_first('div.offer-list-title a').attributes['href']  # type: ignore[assignment]  # 'a' always contains href.
                id_ = int(url.split('/')[-2])
                offers_objs = OfferPreviewsParser(
                    offer_div.html or '',
                    options=self.options.offer_previews_parsing_options,
                ).parse()
                offers[SubcategoryType.get_by_url(url)][id_] = offers_objs  # type: ignore[index] # it is indexable, stupid mypy.
        else:
            offers = None

        return ProfilePage(
            raw_source=self.tree.html or '',
            header=PageHeaderParser(
                self.tree.css_first('header').html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                self.tree.css_first('body').attributes['data-app-data'] or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            user_id=int(
                self.tree.css_first('head > link[rel="canonical"]')  # type: ignore[union-attr] # need to raise an exception if None.
                .attributes['href']
                .split('/')[-2],
            ),
            username=profile_header.css_first('span.mr4').text().strip(),
            badge=badge,
            achievements=[
                AchievementParser(
                    i.html or '',
                    options=self.options.achievement_parsing_options,
                ).parse()
                for i in achievements_divs
            ],
            avatar_url=extract_css_url(
                cast(str, self.tree.css_first('div.avatar-photo').attributes['style']),
            ),
            online='online' in profile_header.css_first('h1.mb40').attributes['class'],  # type: ignore[operator] # always has a class
            banned=banned,
            registration_date_text=(
                reg_date_text_div[0].text(separator='\n', strip=True).strip().split('\n')[-2]
            ),
            status_text=(
                profile_header.css_first('span.media-user-status').text().strip()
                if not banned
                else None
            ),
            rating=UserRatingParser(
                rating_div.html or '',
                options=self.options.user_rating_parsing_options,
            ).parse()
            if rating_div
            else None,
            offers=offers,
            chat=ChatParser(
                chat_div[0].html or '',
                options=self.options.chat_parsing_options,
            ).parse()
            if chat_div
            else None,
            reviews=ReviewsParser(
                reviews_div[0].html or '',
                options=self.options.reviews_parsing_options,
            ).parse()
            if reviews_div
            else None,
        )
