__all__ = ()

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.types.lots import LotPreview, LotSeller
from dataclasses import dataclass


@dataclass(frozen=True)
class LotPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class LotPreviewsParser(FunPayObjectParser[list[LotPreview], LotPreviewsParserOptions]):

    __options_cls__ = FunPayObjectParserOptions

    def _parse(self):
        result = []
        skip_data = ['data-online', 'data-auto']

        for lot_tag in self._tree.xpath('//a[contains(@class, "tc-item")]'):
            additional_data = {}

            price_tag = lot_tag.xpath('.//div[@class="tc-price"][1]')[0]
            user_tag = lot_tag.xpath('.//div[@class="tc-user"][1]')[0]

            username_tag = user_tag.xpath('.//div[@class="media-user-name"][1]/span[1]')[0]
            avatar_tag_style = user_tag.xpath('string(.//div[contains(@class, "avatar-photo")][1]/@style)')

            desc: str | None = lot_tag.xpath('string(.//div[@class="tc-desc-text"][1])').strip() or None
            auto_delivery = bool(lot_tag.get('data-auto'))
            online = bool(lot_tag.get('data-online'))

            lot_id = lot_tag.get('href').split('id=')[1]
            lot_id = int(lot_id) if lot_id.isnumeric() else lot_id

            price = float(price_tag.get('data-s'))
            currency_char = price_tag.xpath('string(.//span[@class="unit"][1])')
            price_dict = MoneyValueDict(value=price, currency_char=currency_char)

            username = username_tag.text
            user_id = int(username_tag.get('data-href').split('/')[-2])

            stars_amount = int(lot_tag.xpath('count(.//i[@class="fas"])'))
            if stars_amount:
                reviews_amount_txt = lot_tag.xpath('string(.//span[@class="rating-mini-count"][1])')
            else:
                reviews_amount_txt = user_tag.xpath('string(.//div[@class="media-user-reviews"][1])')

            reviews_amount = int(reviews_amount_txt) if reviews_amount_txt.isnumeric() else 0
            registration_info = user_tag.xpath('string(.//div[@class="media-user-info"][1])')
            avatar_path = cast(str, parse_avatar_link(avatar_tag_style))

            for key, data in lot_tag.attrib.items():
                if not key.startswith('data-') or key in skip_data:
                    continue
                additional_data[key] = int(data) if data.isnumeric() else data

            user_info = LotUserInfoDict(
                raw_source=html.tostring(user_tag, encoding='unicode'),
                id=user_id,
                nickname=username,
                reviews_amount=reviews_amount,
                rating=stars_amount,
                registration_date_tip=registration_info,
                photo=avatar_path,
                online=online
            )

            lot_obj = LotShortcutDict(
                raw_source=html.tostring(lot_tag, encoding='unicode'),
                id=lot_id,
                desc=desc,
                seller=user_info,
                price=price_dict,
                auto_delivery=auto_delivery,
                data=additional_data
            )

            result.append(lot_obj)

        return LotShortcutsDict(raw_source=self._source, lots=result)