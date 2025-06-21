__all__ = ('LotPreviewsParser', 'LotPreviewsParserOptions')

from copy import deepcopy

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.types.lots import LotPreview, LotSeller
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType
from dataclasses import dataclass
import re
from lxml import html


@dataclass(frozen=True)
class LotPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class LotPreviewsParser(FunPayObjectParser[list[LotPreview], LotPreviewsParserOptions]):

    __options_cls__ = FunPayObjectParserOptions

    def _parse(self):
        result = []
        skip_data = ['data-online', 'data-auto']  # don't add these fields to LotPreview.other_data
        skip_match_data = ['user', 'online', 'auto']  # don't look for human-readable names for this data fields
        processed_users = {}

        for lot_tag in self.tree.xpath('//a[contains(@class, "tc-item")]'):
            lot_id_str = lot_tag.get('href').split('id=')[1]
            desc = lot_tag.xpath('string(.//div[@class="tc-desc-text"][1])').strip() or None

            amount_tag = lot_tag.xpath('.//div[contains(@class, "tc-amount")][1]')
            if amount_tag:
                amount_str = amount_tag[0].get('data-s') or amount_tag[0].xpath('string(.)').strip().replace(' ', '')
                amount = int(amount_str) if amount_str.isnumeric() else None
            else:
                amount = None

            price_tag = lot_tag.xpath('.//div[@class="tc-price"][1]')[0]
            price = MoneyValueParser(html.tostring(price_tag, encoding='unicode'),
                                     options=MoneyValueParserOptions(
                                         parsing_type=MoneyValueParsingType.FROM_LOT_PREVIEW,
                                         parse_value_from_attribute=False if 'chips' in lot_tag.get('href') else True,
                                     ) & self.options).parse()

            seller = self._parse_user_tag(lot_tag, processed_users)

            additional_data = {
                key.replace('data-', ''): int(data) if data.isnumeric() else data
                for key, data in lot_tag.attrib.items()
                if key.startswith('data-') and key not in skip_data
            }

            names = {}
            for data_key in additional_data:
                if data_key in skip_match_data:
                    continue
                div = lot_tag.xpath(f'.//div[contains(@class, "tc-{data_key}")]')
                if not div:
                    continue
                div = div[0]
                names[data_key] = div.xpath('string(.)')

            result.append(LotPreview(
                raw_source=html.tostring(lot_tag, encoding='unicode'),
                id=int(lot_id_str) if lot_id_str.isnumeric() else lot_id_str,
                auto_issue=bool(lot_tag.get('data-auto')),
                is_pinned=bool(lot_tag.get('data-user')),
                desc=desc,
                amount=amount,
                price=price,
                seller=seller,
                other_data=additional_data,
                other_data_names=names
            ))

        return result

    @staticmethod
    def _parse_user_tag(lot_tag, processed_users) -> LotSeller:
        user_tag = lot_tag.xpath('.//div[@class="tc-user"][1]')[0]
        username_tag = user_tag.xpath('.//div[@class="media-user-name"][1]/span[1]')[0]
        user_id = int(username_tag.get('data-href').split('/')[-2])

        if user_id in processed_users:
            return deepcopy(processed_users[user_id])

        avatar_tag_style = user_tag.xpath('string(.//div[contains(@class, "avatar-photo")][1]/@style)')

        stars_amount = int(user_tag.xpath('count(.//i[@class="fas"])'))
        if stars_amount:
            reviews_amount_txt = user_tag.xpath('string(.//span[@class="rating-mini-count"][1])')
        else:
            reviews_amount_txt = user_tag.xpath('string(.//div[@class="media-user-reviews"][1])')

        if reviews_amount_txt.isnumeric():
            reviews_amount = int(reviews_amount_txt)
        else:
            reviews_amount = re.findall(r'\d+', reviews_amount_txt)
            reviews_amount = int(reviews_amount[0]) if reviews_amount else 0

        result = LotSeller(
            raw_source=html.tostring(user_tag, encoding='unicode'),
            id=user_id if user_id is not None else int(username_tag.get('data-href').split('/')[-2]),
            username=username_tag.text.strip(),
            online=bool(lot_tag.get('data-online')),
            avatar_url=extract_css_url(avatar_tag_style),
            register_date_text=user_tag.xpath('string(.//div[@class="media-user-info"][1])'),
            rating=stars_amount,
            reviews_amount=reviews_amount
        )

        processed_users[user_id] = result
        return result
