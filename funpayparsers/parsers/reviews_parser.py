__all__ = (
    'ReviewsParser',
    'ReviewsParserOptions'
)

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.types.review import Review
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType
from funpayparsers.types.common import MoneyValue
from dataclasses import dataclass
from lxml import html
import re


@dataclass(frozen=True)
class ReviewsParserOptions(FunPayObjectParserOptions):
    ...


class ReviewsParser(FunPayObjectParser[
                        list[Review],
                        ReviewsParserOptions
                    ]):

    __options_cls__ = ReviewsParserOptions

    def _parse(self):
        result = []

        for review_div in self.tree.xpath('//div[contains(@class,"review-container")]'):
            order_id, rating = review_div.get('data-order'), review_div.get('data-rating')

            if order_id is not None:
                return self._parse_order_page_review(order_id, rating, review_div)

            inner_review_div = review_div.xpath('.//div[contains(@class, "review-item")][1]')[0]
            date_str, text, game, value = self._parse_review_meta(inner_review_div)
            rating = inner_review_div.xpath('.//div['
                                            'contains(@class, "rating1") or '
                                            'contains(@class, "rating2") or '
                                            'contains(@class, "rating3") or '
                                            'contains(@class, "rating4") or '
                                            'contains(@class, "rating5")][1]')[0]
            rating = int(rating.get('class')[-1])

            order_id = inner_review_div.xpath('.//div[contains(@class, "review-item-order")][1]')
            if order_id:
                order_id = order_id[0].xpath('string(.)').strip().split()[1][1:]
            else:
                order_id = None

            user_tag = inner_review_div.xpath('.//div[contains(@class, "review-item-user")]')[0]
            avatar_url = user_tag.xpath('.//img')[0].get('src')

            user_a = user_tag.xpath('.//a')
            user_link = user_a[0].get('href') if user_a else None
            user_id = int(user_link.split('/')[-2]) if user_link else None
            username = user_tag.xpath('string(.//div[contains(@class, "media-user-name")])').strip() or None

            reply = self._parse_reply(inner_review_div)

            result.append(Review(
                raw_source=html.tostring(review_div, encoding='unicode'),
                rating=rating,
                text=text,
                order_total=value,
                order_category=game,
                sender_username=username,
                sender_id=user_id,
                sender_avatar_url=avatar_url,
                order_id=order_id,
                order_time_string=date_str,
                response=reply
            ))

        return result

    def _parse_order_page_review(self, order_id: str, rating: str, review_div) -> list[Review]:
        inner_review_div = review_div.xpath('.//div[contains(@class, "review-item")][1]')[0]
        author_id = int(
            inner_review_div.xpath('.//div[contains(@class, "review-item-row") and @data-row="review"]')[0]
            .get('data-author')
        )

        if rating:  # if review exists
            rating = int(rating)
            date_str, text, game, value = self._parse_review_meta(inner_review_div)

            user_tag = review_div.xpath('.//div[contains(@class, "review-item-user")]')[0]
            avatar_url = user_tag.xpath('.//img')[0].get('src')

        else:
            rating = text = value = game = avatar_url = date_str = None

        reply = self._parse_reply(inner_review_div)


        return [Review(
            raw_source=html.tostring(review_div, encoding='unicode'),
            rating=rating,
            text=text,
            order_total=value,
            order_category=game,
            sender_username=self.options.context.get('sender_username'),
            sender_id=author_id,
            sender_avatar_url=avatar_url,
            order_id=order_id,
            order_time_string=date_str,
            response=reply
        )]

    def _parse_review_meta(self, review_div) -> tuple[str, str, str, MoneyValue]:
        date_str = review_div.xpath('string(.//div[contains(@class, "review-item-date")][1])').strip()
        text = review_div.xpath('string(.//div[contains(@class, "review-item-text")])')[1:-1]

        review_details_str = review_div.xpath('string(.//div[contains(@class, "review-item-detail")][1])')
        game, value = review_details_str.split(',')
        value = MoneyValueParser(value.strip(), options=MoneyValueParserOptions(
            parsing_type=MoneyValueParsingType.FROM_STRING
        ) & self.options).parse()

        return date_str, text, game, value

    def _parse_reply(self, review_div):
        reply = None
        reply_div = review_div.xpath('.//div[contains(@class, "review-compiled-reply")]/div')
        if not reply_div:
            return None

        reply_div = reply_div[0]
        if not reply_div.attrib:
            reply = reply_div.text.strip()

        return reply