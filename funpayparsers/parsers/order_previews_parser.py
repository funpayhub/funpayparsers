__all__ = ('OrderPreviewsParserOptions', 'OrderPreviewsParser', )

from dataclasses import dataclass

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.types.orders import OrderPreview, OrderCounterpartyInfo, OrderPreviewsBatch
from funpayparsers.types.enums import OrderStatus
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType

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
            status_class = o.xpath('string(.//div[contains(@class, "tc-status")][1]/@class)')

            val_div = o.xpath('.//div[contains(@class, "tc-price")]')[0]
            value = MoneyValueParser(html.tostring(val_div, encoding='unicode'),
                                      options=MoneyValueParserOptions(
                                          parsing_type=MoneyValueParsingType.FROM_ORDER_PREVIEW
                                      ) & self.options).parse()

            user_tag = o.xpath('.//div[contains(@class, "media-user")][1]')[0]
            photo_style = o.xpath('string(.//div[contains(@class, "avatar-photo")]/@style)')
            nickname_tag = user_tag.xpath('.//div[@class="media-user-name"]/span[1]')[0]
            user_status_text: str = user_tag.xpath(
                'string(.//div[contains(@class, "media-user-status")][1])'
            ).strip()

            counterparty = OrderCounterpartyInfo(
                raw_source=html.tostring(user_tag, encoding='unicode'),
                id=int(nickname_tag.get('data-href').split('/')[-2]),
                username=nickname_tag.text.strip(),
                online='online' in user_tag.get('class'),
                avatar_url=extract_css_url(photo_style),
                banned='banned' in user_tag.get('class'),
                status_text=user_status_text
            )

            order_obj = OrderPreview(
                raw_source=html.tostring(o, encoding='unicode'),
                id=o.get('href').split('/')[-2],
                date_text=o.xpath('string(.//div[@class="tc-date-time"][1])'),
                desc=o.xpath('string(.//div[@class="order-desc"][1]/div[1])'),
                category_text=o.xpath('string(.//div[@class="text-muted"][1])'),
                status=OrderStatus.get_by_css_class(status_class),
                total=value,
                counterparty=counterparty
            )
            result.append(order_obj)

        next_id = self.tree.xpath('//input[@type="hidden" and @name="continue"][1]')

        return OrderPreviewsBatch(
            raw_source=self.raw_source,
            orders=result,
            next_order_id=next_id[0].get('value') if next_id else None
        )
