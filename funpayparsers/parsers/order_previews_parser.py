__all__ = ('OrderPreviewsParserOptions', 'OrderPreviewsParser', )

from dataclasses import dataclass

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayHTMLObjectParser
from funpayparsers.types.orders import OrderPreview, OrderPreviewsBatch
from funpayparsers.parsers.user_preview_parser import UserPreviewParser, UserPreviewParserOptions
from funpayparsers.types.enums import OrderStatus
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType


@dataclass(frozen=True)
class OrderPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class OrderPreviewsParser(FunPayHTMLObjectParser[
                              list[OrderPreview],
                              OrderPreviewsParserOptions
                          ]):
    """
    Class for parsing order previews.
    Possible locations:
        - On sales page (https://funpay.com/orders/trade).
        - On purchases page (https://funpay.com/orders/).
    """
    def _parse(self):
        result = []

        for order in self.tree.css('a.tc-item'):
            status_class = order.css('div.tc-status')[0].attributes['class']

            value = MoneyValueParser(raw_source=order.css('div.tc-price')[0].html,
                                      options=MoneyValueParserOptions(
                                          parsing_type=MoneyValueParsingType.FROM_ORDER_PREVIEW
                                      ) & self.options).parse()

            user_tag = order.css('div.media-user')[0]
            counterparty = UserPreviewParser(
                raw_source=user_tag.html,
                options=UserPreviewParserOptions() & self.options
            ).parse()

            order_obj = OrderPreview(
                raw_source=order.html,
                id=order.attributes['href'].split('/')[-2],
                date_text=order.css('div.tc-date-time')[0].text(strip=True),
                desc=order.css('div.order-desc > div')[0].text(deep=False, strip=True),
                category_text=order.css('div.text-muted')[0].text(strip=True),
                status=OrderStatus.get_by_css_class(status_class),
                total=value,
                counterparty=counterparty
            )
            result.append(order_obj)

        next_id = self.tree.css('input[type="hidden"][name="continue"]')

        return OrderPreviewsBatch(
            raw_source=self.raw_source,
            orders=result,
            next_order_id=next_id[0].attributes.get('value') if next_id else None
        )
