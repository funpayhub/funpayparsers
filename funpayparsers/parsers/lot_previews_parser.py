__all__ = ('LotPreviewsParser', 'LotPreviewsParserOptions')

from copy import deepcopy

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayHTML2ObjectParser
from funpayparsers.types.lots import LotPreview, LotSeller
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType
from dataclasses import dataclass
import re
from selectolax.lexbor import LexborNode


@dataclass(frozen=True)
class LotPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class LotPreviewsParser(FunPayHTML2ObjectParser[list[LotPreview], LotPreviewsParserOptions]):
    def _parse(self):
        result = []
        skip_data = ['data-online', 'data-auto']  # don't add these fields to LotPreview.other_data
        skip_match_data = ['user', 'online', 'auto']  # don't look for human-readable names for this data fields
        processed_users = {}

        for lot_tag in self.tree.css('a.tc-item'):
            lot_id_str = lot_tag.attributes['href'].split('id=')[1]
            desc = lot_tag.css('div.tc-desc-text')
            desc = desc[0].text(strip=True) if desc else None

            amount_tag = lot_tag.css('div.tc-amount')
            if amount_tag:
                amount_str = amount_tag[0].attributes.get('data-s') or amount_tag[0].text(strip=True)
                amount = int(amount_str) if amount_str.isnumeric() else None
            else:
                amount = None

            price_tag = lot_tag.css('div.tc-price')[0]
            price = MoneyValueParser(price_tag.html,
                                     options=MoneyValueParserOptions(
                                         parsing_type=MoneyValueParsingType.FROM_LOT_PREVIEW,
                                         parse_value_from_attribute=False if 'chips' in lot_tag.attributes['href'] else True,
                                     ) & self.options).parse()

            seller = self._parse_user_tag(lot_tag, processed_users)

            additional_data = {
                key.replace('data-', ''): int(data) if data.isnumeric() else data
                for key, data in lot_tag.attrs.items()
                if key.startswith('data-') and key not in skip_data
            }

            names = {}
            for data_key in additional_data:
                if data_key in skip_match_data:
                    continue
                div = lot_tag.css(f'div.tc-{data_key}')
                if not div:
                    continue
                div = div[0]
                names[data_key] = div.text(strip=True)

            result.append(LotPreview(
                raw_source=lot_tag.html,
                id=int(lot_id_str) if lot_id_str.isnumeric() else lot_id_str,
                auto_issue=bool(lot_tag.attrs.get('data-auto')),
                is_pinned=bool(lot_tag.attrs.get('data-user')),
                desc=desc,
                amount=amount,
                price=price,
                seller=seller,
                other_data=additional_data,
                other_data_names=names
            ))

        return result

    @staticmethod
    def _parse_user_tag(lot_tag: LexborNode, processed_users) -> LotSeller | None:
        user_tag = lot_tag.css('div.tc-user')
        if not user_tag:  # if this is LotPreview from sellers page, not from subcategory lots page
            return None

        user_tag = user_tag[0]
        username_tag = user_tag.css('div.media-user-name > span')[0]
        user_id = int(username_tag.attributes['data-href'].split('/')[-2])

        if user_id in processed_users:
            return deepcopy(processed_users[user_id])

        avatar_tag_style = user_tag.css('div.avatar-photo')[0].attributes['style']

        stars_amount = len(user_tag.css('i.fas'))
        if stars_amount:
            reviews_amount_txt = user_tag.css('span.rating-mini-count')[0].text(deep=True, strip=True)
        else:
            reviews_amount_txt = user_tag.css('div.media-user-reviews')[0].text(deep=True, strip=True)

        if reviews_amount_txt.isnumeric():
            reviews_amount = int(reviews_amount_txt)
        else:
            reviews_amount = re.findall(r'\d+', reviews_amount_txt)
            reviews_amount = int(reviews_amount[0]) if reviews_amount else 0

        result = LotSeller(
            raw_source=user_tag.html,
            id=user_id if user_id is not None else int(username_tag.attributes['data-href'].split('/')[-2]),
            username=username_tag.text(strip=True),
            online=bool(lot_tag.attributes.get('data-online')),
            avatar_url=extract_css_url(avatar_tag_style),
            register_date_text=user_tag.css('div.media-user-info')[0].text(deep=True, strip=True),
            rating=stars_amount,
            reviews_amount=reviews_amount
        )

        processed_users[user_id] = result
        return result
