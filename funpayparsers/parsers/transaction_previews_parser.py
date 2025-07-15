from __future__ import annotations


__all__ = ('TransactionPreviewsParser', 'TransactionPreviewsParsingOptions')

from typing import cast
from dataclasses import dataclass

from funpayparsers.types.enums import PaymentMethod, TransactionStatus
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.finances import TransactionPreview, TransactionPreviewsBatch
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)


@dataclass(frozen=True)
class TransactionPreviewsParsingOptions(ParsingOptions):
    """Options class for ``ReviewsParser``."""

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``ReviewsParser``.
    
    ``parsing_mode`` option is hardcoded in ``TransactionPreviewsParser`` 
    and is therefore ignored if provided externally.

    Defaults to ``UserPreviewParsingOptions()``.
    """


class TransactionPreviewsParser(
    FunPayHTMLObjectParser[
        TransactionPreviewsBatch,
        TransactionPreviewsParsingOptions,
    ]
):
    """
    Class for parsing transaction previews.

    Possible locations:
        - Transactions page (https://funpay.com/account/balance).
    """

    def _parse(self) -> TransactionPreviewsBatch:
        result = []
        for i in self.tree.css('div.tc-item'):
            value = MoneyValueParser(
                raw_source=i.css('div.tc-price')[0].html or '',
                options=self.options.money_value_parsing_options,
                parsing_mode=MoneyValueParsingMode.FROM_TRANSACTION_PREVIEW,
            ).parse()
            recipient_div = i.css('span.tc-payment-number')

            payment_method_divs = i.css('span.payment-logo')
            payment_method = (
                PaymentMethod.get_by_css_class(
                    payment_method_divs[0].attributes['class'],  # type: ignore[arg-type]
                    # always has a class
                )
                if payment_method_divs
                else None
            )

            result.append(
                TransactionPreview(
                    raw_source=i.html or '',
                    id=int(cast(str, i.attributes['data-transaction'])),
                    date_text=i.css('span.tc-date-time')[0].text(strip=True),
                    desc=i.css('span.tc-title')[0].text(strip=True),
                    status=TransactionStatus.get_by_css_class(cast(str, i.attributes['class'])),
                    amount=value,
                    payment_method=payment_method,
                    withdrawal_number=(
                        recipient_div[0].text(strip=True) if recipient_div else None
                    ),
                )
            )

        user_id = self.tree.css('input[type="hidden"][name="user_id"]')
        filter_ = self.tree.css('input[type="hidden"][name="filter"]')
        next_id = self.tree.css('input[type="hidden"][name="continue"]')

        return TransactionPreviewsBatch(
            raw_source=self.raw_source,
            transactions=result,
            user_id=int(cast(str, user_id[0].attributes.get('value'))) if user_id else None,
            filter=filter_[0].attributes.get('value') if filter_ else None,
            next_transaction_id=int(cast(str, next_id[0].attributes.get('value')))
            if next_id
            else None,
        )
