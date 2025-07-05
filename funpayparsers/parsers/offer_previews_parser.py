__all__ = ('OfferPreviewsParser', 'OfferPreviewsParserOptions')

from copy import deepcopy

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferPreview, OfferSeller
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType
from dataclasses import dataclass
import re
from selectolax.lexbor import LexborNode


@dataclass(frozen=True)
class OfferPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class OfferPreviewsParser(FunPayHTMLObjectParser[list[OfferPreview], OfferPreviewsParserOptions]):
    """
    Class for parsing public offer previews.
    Possible locations:
        - On sellers pages (https://funpay.com/<userid>/).
        - On subcategories offer list pages (https://funpay.com/<lots/chips>/<subcategory_id>).
    """
    def _parse(self):
        result = []

        # don't add these data-fields to OfferPreview.other_data,
        # cz there are specific fields in OfferPreview class for them.
        skip_data = ['data-online', 'data-auto']

        # don't look for these human-readable names for this data-fields,
        # cz there are specific fields in OfferPreview class for them.
        skip_match_data = ['user', 'online', 'auto']

        processed_users = {}

        for offer_div in self.tree.css('a.tc-item'):
            offer_id_str = offer_div.attributes['href'].split('id=')[1]
            desc = offer_div.css('div.tc-desc-text')
            desc = desc[0].text(strip=True) if desc else None  # currency offers don't have description.

            # Currency offers have 'data-s' attribute in tc-amount div, where amount is stored.
            # Common offers don't have it, so we need to parse tc-amount divs text.
            # Common offers don't have tc-amount div, if the seller didn't specify the amount of goods.
            amount_div = offer_div.css('div.tc-amount')
            if amount_div:
                amount_str = amount_div[0].attributes.get('data-s') or amount_div[0].text(strip=True)
                amount = int(amount_str) if amount_str.isnumeric() else None
            else:
                amount = None

            price_div = offer_div.css('div.tc-price')[0]
            price = MoneyValueParser(price_div.html,
                                     options=MoneyValueParserOptions(
                                         parsing_type=MoneyValueParsingType.FROM_OFFER_PREVIEW,
                                         parse_value_from_attribute=False if 'chips' in offer_div.attributes['href'] else True,
                                     ) & self.options).parse()

            seller = self._parse_user_tag(offer_div, processed_users)

            additional_data = {
                key.replace('data-', ''): int(data) if data.isnumeric() else data
                for key, data in offer_div.attributes.items()
                if key.startswith('data-') and key not in skip_data
            }

            names = {}
            for data_key in additional_data:
                if data_key in skip_match_data:
                    continue
                div = offer_div.css(f'div.tc-{data_key}')
                if not div:
                    continue
                div = div[0]
                names[data_key] = div.text(strip=True)

            result.append(OfferPreview(
                raw_source=offer_div.html,
                id=int(offer_id_str) if offer_id_str.isnumeric() else offer_id_str,
                auto_delivery=bool(offer_div.attributes.get('data-auto')),
                is_pinned=bool(offer_div.attributes.get('data-user')),
                desc=desc,
                amount=amount,
                price=price,
                seller=seller,
                other_data=additional_data,
                other_data_names=names
            ))

        return result

    @staticmethod
    def _parse_user_tag(offer_tag: LexborNode, processed_users) -> OfferSeller | None:
        # If this offer preview is from sellers page, and not from subcategory offers page,
        # there is no user div.
        user_div = offer_tag.css('div.tc-user')
        if not user_div:
            return None

        user_div = user_div[0]
        username_span = user_div.css('div.media-user-name > span')[0]
        user_id = int(username_span.attributes['data-href'].split('/')[-2])

        if user_id in processed_users:
            return deepcopy(processed_users[user_id])

        avatar_tag_style = user_div.css('div.avatar-photo')[0].attributes['style']

        # If the user has fewer than 10 reviews or registered less than a month ago,
        # the rating stars are not shown. The number of reviews is displayed
        # as "N reviews" (or "No reviews" if there are none).
        # Otherwise, the user sees rating stars along with the number of reviews next to them.
        stars_amount = len(user_div.css('i.fas'))
        if stars_amount:
            reviews_amount = int(user_div.css('span.rating-mini-count')[0].text(deep=True, strip=True))
        else:
            reviews_amount_txt = user_div.css('div.media-user-reviews')[0].text(deep=True, strip=True)
            reviews_amount = re.findall(r'\d+', reviews_amount_txt)
            reviews_amount = int(reviews_amount[0]) if reviews_amount else 0

        result = OfferSeller(
            raw_source=user_div.html,
            id=user_id if user_id is not None else int(username_span.attributes['data-href'].split('/')[-2]),
            username=username_span.text(strip=True),
            online=bool(offer_tag.attributes.get('data-online')),
            avatar_url=extract_css_url(avatar_tag_style),
            register_date_text=user_div.css('div.media-user-info')[0].text(deep=True, strip=True),
            rating=stars_amount,
            reviews_amount=reviews_amount
        )

        processed_users[user_id] = result
        return result
