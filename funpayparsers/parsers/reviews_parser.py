from __future__ import annotations


__all__ = (
    'ReviewsParser',
    'ReviewsParsingOptions',
)

from typing import cast
from dataclasses import dataclass

from selectolax.lexbor import LexborNode

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.reviews import Review, ReviewsBatch
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)


@dataclass(frozen=True)
class ReviewsParsingOptions(ParsingOptions):
    """Options class for ``ReviewsParser``."""

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``ReviewsParser``.
    
    ``parsing_mode`` option is hardcoded in ``ReviewsParser`` and is therefore ignored 
    if provided externally.

    Defaults to ``UserPreviewParsingOptions()``.
    """


class ReviewsParser(FunPayHTMLObjectParser[ReviewsBatch, ReviewsParsingOptions]):
    """
    Class for parsing reviews.

    Possible locations:
        - User profile pages (`https://funpay.com/<userid>/`).
        - Order pages (`https://funpay.com/orders/<orderid>/`)
    """

    def _parse(self) -> ReviewsBatch:
        result: list[Review] = []

        for review_div in self.tree.css('div.review-container'):
            order_id = review_div.attributes.get('data-order')

            if order_id is not None:
                rating_str = review_div.attributes.get('data-rating')
                return ReviewsBatch(
                    raw_source=self.raw_source,
                    reviews=[self._parse_order_page_review(order_id, rating_str, review_div)],
                    user_id=None,
                    filter=None,
                    next_review_id=None,
                )

            result.append(self._parse_common_review(review_div))

        user_id = self.tree.css('input[type="hidden"][name="user_id"]')
        filter_ = self.tree.css('input[type="hidden"][name="filter"]')
        next_id = self.tree.css('input[type="hidden"][name="continue"]')

        return ReviewsBatch(
            raw_source=self.raw_source,
            reviews=result,
            user_id=int(
                user_id[0].attributes.get('value')  # type: ignore[arg-type] # always has value
            )
            if user_id
            else None,
            filter=filter_[0].attributes.get('value') if filter_ else None,
            next_review_id=next_id[0].attributes.get('value') if next_id else None,
        )

    def _parse_common_review(self, review_div: LexborNode) -> Review:
        date_str, text, game, value = self._parse_review_meta(review_div)
        rating_divs = review_div.css(','.join(f'div.rating{i}' for i in range(1, 5 + 1)))

        # old reviews might have no rating
        rating = int(cast(str, rating_divs[0].attributes['class'])[-1]) if rating_divs else None

        order_id_div = review_div.css('div.review-item-order')

        # "Order #ORDERID"
        order_id = None if not order_id_div else order_id_div[0].text().strip().split()[1][1:]

        user_tag = review_div.css('div.review-item-user')[0]
        usernames = user_tag.css('div.media-user-name')
        username = usernames[0].text().strip() if usernames else None

        return Review(
            raw_source=review_div.html or '',
            rating=rating,
            text=text.strip(),
            order_total=value,
            category_str=game,
            sender_username=username,
            sender_id=int(
                user_tag.css('a')[0].attributes['href'].split('/')[-2],  # type: ignore[union-attr]
                # always has href
            )
            if username
            else None,
            sender_avatar_url=user_tag.css('img')[0].attributes['src'],
            order_id=order_id,
            date_text=date_str,
            reply=self._parse_reply(review_div),
        )

    def _parse_order_page_review(
        self, order_id: str, rating_str: str | None, review_div: LexborNode
    ) -> Review:
        author_id_str: str = review_div.css('div.review-item-row[data-row="review"]')[
            0
        ].attributes.get('data-author')  # type: ignore[assignment]  # always has data-author
        author_id = int(author_id_str)

        if rating_str:  # if review exists
            rating = int(rating_str)
            date_str, text, game, value = self._parse_review_meta(review_div)

            user_tag = review_div.css('div.review-item-user')[0]
            avatar_url = user_tag.css('img')[0].attributes['src']

        else:
            rating = text = value = game = avatar_url = date_str = None  # type: ignore[assignment]

        return Review(
            raw_source=review_div.html or '',
            rating=rating,
            text=text,
            order_total=value,
            category_str=game,
            sender_username=self.options.context.get('sender_username'),
            sender_id=author_id,
            sender_avatar_url=avatar_url,
            order_id=order_id,
            date_text=date_str,
            reply=self._parse_reply(review_div),
        )

    def _parse_review_meta(self, review_div: LexborNode) -> tuple[str, str, str, MoneyValue]:
        date_str = review_div.css('div.review-item-date')[0].text().strip()
        text = review_div.css('div.review-item-text')[0].text().strip()

        review_details_str = review_div.css('div.review-item-detail')[0].text().strip()
        split = review_details_str.split(', ')
        game, value = ', '.join(split[:-1]), split[-1]
        money_value = MoneyValueParser(
            raw_source=value.strip(),
            options=self.options.money_value_parsing_options,
            parsing_mode=MoneyValueParsingMode.FROM_STRING,
        ).parse()

        return date_str, text, game, money_value

    def _parse_reply(self, review_div: LexborNode) -> str | None:
        reply = None
        reply_divs = review_div.css('div.review-compiled-reply > div:not([class])')
        if not reply_divs:
            return None

        reply_div = reply_divs[0]
        if not reply_div.attributes.items():
            reply = reply_div.text().strip()

        return reply
