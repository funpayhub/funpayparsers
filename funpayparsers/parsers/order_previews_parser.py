__all__ = ('OrderPreviewsParserOptions', 'OrderPreviewsParser', )

from dataclasses import dataclass

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.parsers.utils import extract_css_url, parse_money_value_string
from funpayparsers.types.orders import OrderPreview, OrderCounterpartyInfo
from funpayparsers.types.enums import OrderStatus

from lxml import html


@dataclass(frozen=True)
class OrderPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class OrderPreviewsParser(FunPayObjectParser[
                              list[OrderPreview],
                              OrderPreviewsParserOptions
                          ]):
    __options_cls__ = OrderPreviewsParserOptions

    def _parse(self):
        result = []

        for o in self.tree.xpath('//a[contains(@class, "tc-item")]'):
            order_id: str = o.get('href').split('/')[-2]
            date: str = o.xpath('string(.//div[@class="tc-date-time"][1])')

            desc = o.xpath('string(.//div[@class="order-desc"][1]/div[1])')
            category_desc = o.xpath('string(.//div[@class="text-muted"][1])')

            status_class = o.xpath('string(.//div[contains(@class, "tc-status")][1]/@class)')
            status = OrderStatus.get_by_css_class(status_class)

            val_str = o.xpath('string(.//div[contains(@class, "tc-price")])')
            value = parse_money_value_string(val_str)

            user_tag = o.xpath('.//div[contains(@class, "media-user")][1]')[0]
            photo_style = o.xpath(
                'string(.//div[contains(@class, "avatar-photo")]/@style)')
            nickname_tag = user_tag.xpath('.//div[@class="media-user-name"]/span[1]')[0]
            user_nickname = nickname_tag.text
            user_id = int(nickname_tag.get('data-href').split('/')[-2])
            online = 'online' in user_tag.get('class')
            banned = 'banned' in user_tag.get('class')
            user_status_text: str = user_tag.xpath(
                'string(.//div[contains(@class, "media-user-status")][1])'
            )
            photo_url = extract_css_url(photo_style)

            counterparty = OrderCounterpartyInfo(
                raw_source=html.tostring(user_tag, encoding='unicode'),
                id=user_id,
                username=user_nickname,
                online=online,
                avatar_url=photo_url,
                banned=banned,
                status_text=user_status_text
            )

            order_obj = OrderPreview(
                raw_source=html.tostring(o, encoding='unicode'),
                id=order_id,
                date_text=date,
                desc=desc,
                category_text=category_desc,
                status=status,
                amount=value,
                counterparty=counterparty
            )
            result.append(order_obj)

        return result