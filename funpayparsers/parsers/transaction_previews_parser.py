__all__ = ('TransactionPreviewsParser', 'TransactionPreviewsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.types.finances import TransactionPreview, TransactionPreviewsBatch
from funpayparsers.types.enums import TransactionStatus, PaymentMethod
from funpayparsers.parsers.money_value_parser import MoneyValueParserOptions, MoneyValueParsingType, MoneyValueParser


@dataclass(frozen=True)
class TransactionPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class TransactionPreviewsParser(FunPayHTMLObjectParser[
    TransactionPreviewsBatch,
    TransactionPreviewsParserOptions
]):
    """
    Class for parsing transaction previews.
    Possible locations:
        - On transactions page (https://funpay.com/account/balance).
    """
    def _parse(self):
        result = []
        for i in self.tree.css('div.tc-item'):
            value = MoneyValueParser(raw_source=i.css('div.tc-price')[0].html,
                                     options=MoneyValueParserOptions(
                                         parsing_type=MoneyValueParsingType.FROM_TRANSACTION_PREVIEW
                                     ) & self.options).parse()
            recipient_div = i.css('span.tc-payment-number')

            payment_method = i.css('span.payment-logo')
            payment_method = PaymentMethod.get_by_css_class(payment_method[0].attributes['class']) if payment_method else None

            result.append(TransactionPreview(
                raw_source=i.html,
                id=int(i.attributes['data-transaction']),
                date_text=i.css('span.tc-date-time')[0].text(strip=True),
                desc=i.css('span.tc-title')[0].text(strip=True),
                status=TransactionStatus.get_by_css_class(i.attributes['class']),
                amount=value,
                payment_method=payment_method,
                withdrawal_number=recipient_div[0].text(strip=True) if recipient_div else None,
            ))

        user_id = self.tree.css('input[type="hidden"][name="user_id"]')
        filter_ = self.tree.css('input[type="hidden"][name="filter"]')
        next_id = self.tree.css('input[type="hidden"][name="continue"]')

        return TransactionPreviewsBatch(
            raw_source=self.raw_source,
            transactions=result,
            user_id = int(user_id[0].attributes.get('value')) if user_id else None,
            filter = filter_[0].attributes.get('value') if filter_ else None,
            next_transaction_id= int(next_id[0].attributes.get('value')) if next_id else None
        )
