from __future__ import annotations


__all__ = ('UserRatingParsingOptions', 'UserRatingParser')


import re
from dataclasses import dataclass
from enum import Enum

from selectolax.lexbor import LexborNode

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import UserRating


class UserRatingParsingMode(Enum):
    """``UserRatingParser`` parsing modes enumeration."""

    FROM_PROFILE_HEADER = 0
    """Raw source is/from a profile header."""

    FROM_REVIEWS_SECTION = 1
    """Raw source is/from a reviews section header."""


@dataclass(frozen=True)
class UserRatingParsingOptions(ParsingOptions):
    """Options class for ``UserRatingParser``."""

    parsing_mode: UserRatingParsingMode = UserRatingParsingMode.FROM_REVIEWS_SECTION
    """
    ``UserRatingParser`` parsing mode.

    It is recommended to parse the user rating from the reviews section, 
    because some profiles contain legacy reviews that do not include a rating. 
    If a user has only such reviews, 
    the profile header will not include the rating block.
    However, the reviews section always contains a rating block as long as there is 
    at least one review of any type.

    Defaults to ``UserRatingParsingMode.FROM_REVIEWS_SECTION``.
    """


class UserRatingParser(FunPayHTMLObjectParser[UserRating, UserRatingParsingOptions]):
    """
    Class for parsing user rating.

    Possible locations:
        - User profile pages (`https://funpay.com/<userid>/`).
    """

    def _parse(self) -> UserRating:
        if self.options.parsing_mode == UserRatingParsingMode.FROM_PROFILE_HEADER:
            return self._parse_from_profile_header()
        return self._parse_from_reviews_section()

    def _parse_from_profile_header(self) -> UserRating:
        rating_div = self.tree.css('div.profile-header-col-rating')[0]

        stars_text = rating_div.css('div.rating-value > span.big')[0].text().strip()
        try:
            stars = float(stars_text)
        except ValueError:
            stars = 0.0

        percentage = self._parse_percentage(rating_div)

        reviews_text = rating_div.css('div.rating-full-count')[0].text().replace(' ', '')
        match = re.search(r'\d+', reviews_text)
        reviews_amount = int(match.group())  # type: ignore[union-attr] # always has \d+

        return UserRating(
            raw_source=rating_div.html or '',
            stars=stars,
            reviews_amount=reviews_amount,
            five_star_reviews_percentage=percentage[4],
            four_star_reviews_percentage=percentage[3],
            three_star_reviews_percentage=percentage[2],
            two_star_reviews_percentage=percentage[1],
            one_star_reviews_percentage=percentage[0],
        )

    def _parse_from_reviews_section(self) -> UserRating:
        rating_div = self.tree.css_first('div.param-item.mb10')
        stars_text = rating_div.css('div.rating-value > span.big')[0].text().strip()
        try:
            stars = float(stars_text)
        except ValueError:
            stars = 0.0

        percentage = self._parse_percentage(rating_div)

        reviews_text = rating_div.css_first('div.mb5').text().replace(' ', '')
        match = re.search(r'\d+', reviews_text)
        reviews_amount = int(match.group())  # type: ignore[union-attr] # always has \d+

        return UserRating(
            raw_source=rating_div.html or '',
            stars=stars,
            reviews_amount=reviews_amount,
            five_star_reviews_percentage=percentage[4],
            four_star_reviews_percentage=percentage[3],
            three_star_reviews_percentage=percentage[2],
            two_star_reviews_percentage=percentage[1],
            one_star_reviews_percentage=percentage[0],
        )

    def _parse_percentage(self, rating_div: LexborNode) -> list[float]:
        percentage: list[float] = []
        for i in range(1, 6):
            style: str = rating_div.css(f'div.rating-full-item{i} > div.rating-progress > div')[
                0
            ].attributes['style']  # type: ignore[assignment]  # always has a style
            value = re.search(r'\d+', style)
            percentage.append(float(value.group()))  # type: ignore[union-attr] # always has \d+

        return percentage
