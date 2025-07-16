from __future__ import annotations


__all__ = ('OrderPreviewsParsingOptions', 'OrderPreviewsParser')

from dataclasses import dataclass

from funpayparsers.types.enums import OrderStatus
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.orders import OrderPreview, OrderPreviewsBatch
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)
from funpayparsers.parsers.user_preview_parser import (
    UserPreviewParser,
    UserPreviewParsingMode,
    UserPreviewParsingOptions,
)


@dataclass(frozen=True)
class OrderPreviewsParsingOptions(ParsingOptions):
    """Options class for ``OrderPreviewsParser``."""

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``OrderPreviewsParser``.
    
    ``parsing_mode`` option is hardcoded in ``OrderPreviewsParser`` 
    and is therefore ignored if provided externally.

    Defaults to ``UserPreviewParsingOptions()``.
    """

    user_preview_parsing_options: UserPreviewParsingOptions = UserPreviewParsingOptions()
    """
    Options instance for ``UserPreviewParsingOptions``, 
    which is used by ``OrderPreviewsParser``.
    
    ``parsing_mode`` option is hardcoded in ``OrderPreviewsParser`` 
    and is therefore ignored  if provided externally.

    Defaults to ``UserPreviewParsingOptions()``.
    """


class OrderPreviewsParser(
    FunPayHTMLObjectParser[
        OrderPreviewsBatch,
        OrderPreviewsParsingOptions,
    ]
):
    """
    Class for parsing order previews.

    Possible locations:
        - Sales page (https://funpay.com/orders/trade).
        - Purchases page (https://funpay.com/orders/).
    """

    def _parse(self) -> OrderPreviewsBatch:
        result = []

        for order in self.tree.css('a.tc-item'):
            status_class: str = order.css('div.tc-status')[0].attributes['class']  # type: ignore[assignment] # always has a class

            value = MoneyValueParser(
                order.css('div.tc-price')[0].html or '',
                options=self.options.money_value_parsing_options,
                parsing_mode=MoneyValueParsingMode.FROM_ORDER_PREVIEW,
            ).parse()

            user_tag = order.css('div.media-user')[0]
            counterparty = UserPreviewParser(
                user_tag.html or '',
                options=self.options.user_preview_parsing_options,
                parsing_mode=UserPreviewParsingMode.FROM_ORDER_PREVIEW,
            ).parse()

            result.append(
                OrderPreview(
                    raw_source=order.html or '',
                    id=order.attributes['href'].split('/')[-2],  # type: ignore[union-attr]
                    # always has href
                    date_text=order.css('div.tc-date-time')[0].text(strip=True),
                    title=order.css('div.order-desc > div')[0].text(deep=False, strip=True),
                    category_text=order.css('div.text-muted')[0].text(strip=True),
                    status=OrderStatus.get_by_css_class(status_class),
                    total=value,
                    counterparty=counterparty,
                )
            )

        next_id = self.tree.css('input[type="hidden"][name="continue"]')

        return OrderPreviewsBatch(
            raw_source=self.raw_source,
            orders=result,
            next_order_id=next_id[0].attributes.get('value') if next_id else None,
        )
