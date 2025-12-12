from __future__ import annotations


__all__ = ('OfferPreviewsParser', 'OfferPreviewsParsingOptions')

import re
from dataclasses import dataclass
from copy import deepcopy

from selectolax.lexbor import LexborNode

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferSeller, OfferPreview
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)


@dataclass(frozen=True)
class OfferPreviewsParsingOptions(ParsingOptions):
    """Options class for ``OfferPreviewsParser``."""

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``OfferPreviewsParser``.
    
    ``parsing_mode`` and ``parse_value_from_attribute`` options are hardcoded in 
    ``OfferPreviewsParser`` and is therefore ignored if provided externally.

    Defaults to ``UserPreviewParsingOptions()``.
    """


class OfferPreviewsParser(
    FunPayHTMLObjectParser[list[OfferPreview], OfferPreviewsParsingOptions],
):
    """
    Class for parsing public offer previews.

    Possible locations:
        - User profile pages (https://funpay.com/<userid>/).
        - On subcategories offer list pages
        (https://funpay.com/<lots/chips>/<subcategory_id>).
    """

    def _parse(self) -> list[OfferPreview]:
        result = []

        # don't add these data-fields to OfferPreview.other_data,
        # cz there are specific fields in OfferPreview class for them.
        skip_data = ['data-online', 'data-auto']

        # don't look for these human-readable names for this data-fields,
        # cz there are specific fields in OfferPreview class for them.
        skip_match_data = ['user', 'online', 'auto']

        processed_users: dict[str, OfferSeller] = {}

        for offer_div in self.tree.css('a.tc-item'):
            url: str = offer_div.attributes['href']  # type: ignore[assignment] # always has href
            offer_id_str = url.split('id=')[1]
            desc_divs = offer_div.css('div.tc-desc-text')
            # currency offers don't have description.
            desc = desc_divs[0].text(strip=True) if desc_divs else None

            # Currency offers have 'data-s' attribute in tc-amount div,
            # where amount is stored.
            #
            # Common offers don't have it, so we need to parse tc-amount divs text.
            #
            # Common offers don't have tc-amount div, if the seller didn't
            # specify the amount of goods.
            amount_div = offer_div.css('div.tc-amount')
            if amount_div:
                amount_str = amount_div[0].attributes.get('data-s') or amount_div[0].text(
                    strip=True
                )
                amount = int(amount_str) if amount_str.isnumeric() else None
            else:
                amount = None

            price_div = offer_div.css('div.tc-price')[0]
            price = MoneyValueParser(
                price_div.html or '',
                options=self.options.money_value_parsing_options,
                parsing_mode=MoneyValueParsingMode.FROM_OFFER_PREVIEW,
                parse_value_from_attribute=(
                    False if 'chips' in offer_div.attributes['href'] else True  # type: ignore[operator]
                ),
            ).parse()

            seller = self._parse_user_tag(offer_div, processed_users)

            additional_data: dict[str, str | int] = {}
            for key, data in offer_div.attributes.items():
                if not key.startswith('data-') or key in skip_data:
                    continue
                if data is None:
                    continue
                additional_data[key.replace('data-', '')] = (
                    (int(data)) if data.isnumeric() else data
                )

            names = {}
            for data_key in additional_data:
                if data_key in skip_match_data:
                    continue
                divs = offer_div.css(f'div.tc-{data_key}')
                if not divs:
                    continue
                names[data_key] = divs[0].text(strip=True)

            result.append(
                OfferPreview(
                    raw_source=offer_div.html or '',
                    id=int(offer_id_str) if offer_id_str.isnumeric() else offer_id_str,
                    auto_delivery=bool(offer_div.attributes.get('data-auto')),
                    is_pinned=bool(offer_div.attributes.get('data-user')),
                    title=desc,
                    amount=amount,
                    price=price,
                    seller=seller,
                    other_data=additional_data,
                    other_data_names=names,
                    disabled='warning' in (offer_div.attributes.get('class') or ''),
                )
            )

        return result

    @staticmethod
    def _parse_user_tag(
        offer_tag: LexborNode, processed_users: dict[str, OfferSeller]
    ) -> OfferSeller | None:
        # If this offer preview is from sellers page,
        # and not from subcategory offers page, there is no user div.
        user_divs = offer_tag.css('div.tc-user')
        if not user_divs:
            return None

        user_div = user_divs[0]
        username = user_div.css('div.media-user-name')[0].text(strip=True)
        if username in processed_users:
            return deepcopy(processed_users[username])

        avatar_tag = user_div.css_first('div.avatar-photo')
        user_id = int(avatar_tag.attributes['data-href'].split('/')[-2])  # type: ignore[union-attr]
        # always has data-href
        avatar_tag_style: str = avatar_tag.attributes['style']  # type: ignore[assignment]  # always has style

        # If the user has fewer than 10 reviews or registered less than a month ago,
        # the rating stars are not shown. The number of reviews is displayed
        # as "N reviews" (or "No reviews" if there are none).
        # Otherwise, the user sees rating stars along with the number
        # of reviews next to them.
        stars_amount = len(user_div.css('i.fas'))
        if stars_amount:
            reviews_amount = int(
                user_div.css('span.rating-mini-count')[0].text(deep=True, strip=True)
            )
        else:
            reviews_amount_txt = user_div.css('div.media-user-reviews')[0].text(
                deep=True, strip=True
            )
            reviews_amount_find = re.findall(r'\d+', reviews_amount_txt)
            reviews_amount = int(reviews_amount_find[0]) if reviews_amount_find else 0

        result = OfferSeller(
            raw_source=user_div.html or '',
            id=user_id,
            username=username,
            online=bool(offer_tag.attributes.get('data-online')),
            avatar_url=extract_css_url(avatar_tag_style),
            registration_date_text=(
                user_div.css('div.media-user-info')[0].text(deep=True, strip=True)
            ),
            rating=stars_amount,
            reviews_amount=reviews_amount,
        )

        processed_users[username] = result
        return result
