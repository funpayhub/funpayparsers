__all__ = ('UserRatingParserOptions', 'UserRatingParser')


from dataclasses import dataclass
import re
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.types.common import UserRating


@dataclass(frozen=True)
class UserRatingParserOptions(FunPayObjectParserOptions):
    ...


class UserRatingParser(FunPayHTMLObjectParser[UserRating, UserRatingParserOptions]):
    """
    Class for parsing user rating.
    Possible locations:
        - On sellers pages (https://funpay.com/<userid>/).
    """

    def _parse(self):
        rating_div = self.tree.css('div.profile-header-col-rating')[0]

        stars = rating_div.css('div.rating-value > span.big')[0].text().strip()
        try:
            stars = float(stars)
        except ValueError:
            stars = 0.0

        percentage = []
        for i in range(1, 6):
            value = re.search(r'\d+', rating_div.css(f'div.rating-full-item{i} > div.rating-progress > div')[0].attributes['style'])
            percentage.append(float(value.group()))

        reviews_text = rating_div.css('div.rating-full-count')[0].text()
        match = re.search(r'\d+', reviews_text.replace(' ', ''))
        reviews_amount = int(match.group())

        return UserRating(
            raw_source=rating_div.html,
            stars=stars,
            reviews_amount=reviews_amount,
            five_star_reviews_percentage=percentage[4],
            four_star_reviews_percentage=percentage[3],
            three_star_reviews_percentage=percentage[2],
            two_star_reviews_percentage=percentage[1],
            one_star_reviews_percentage=percentage[0],
        )
