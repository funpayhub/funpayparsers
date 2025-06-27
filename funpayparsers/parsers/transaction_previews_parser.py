__all__ = ('TransactionPreviewsParser', 'TransactionPreviewsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.types.finances import TransactionPreview, TransactionPreviewsBatch
from funpayparsers.types.enums import TransactionStatus, PaymentMethod
from funpayparsers.parsers.money_value_parser import MoneyValueParserOptions, MoneyValueParsingType, MoneyValueParser

from lxml import html


@dataclass(frozen=True)
class TransactionPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class TransactionPreviewsParser(FunPayObjectParser[
    TransactionPreviewsBatch,
    TransactionPreviewsParserOptions
]):

    __options_cls__ = TransactionPreviewsParserOptions

    def _parse(self):
        result = []
        for i in self.tree.xpath('//div[contains(@class, "tc-item")]'):
            id_ = int(i.get('data-transaction'))
            transaction_class_name = i.get('class')

            desc: str = i.xpath('string(.//span[@class="tc-title"][1])')
            date: str = i.xpath('string(.//span[@class="tc-date-time"][1])').strip()

            val_div = i.xpath('.//div[@class="tc-price"]')[0]
            parser = MoneyValueParser(html.tostring(val_div, encoding='unicode'),
                                      options=MoneyValueParserOptions(
                                          parsing_type=MoneyValueParsingType.FROM_TRANSACTION_PREVIEW
                                      ) & self.options)
            value = parser.parse()

            recipient = i.xpath('string(.//span[@class="tc-payment-number"][1])') or None

            payment_method = i.xpath('string(.//span[contains(@class, "payment-logo")][1]/@class)')
            payment_method = None if not payment_method else PaymentMethod.get_by_css_class(payment_method)

            result.append(TransactionPreview(
                raw_source=html.tostring(i, encoding='unicode'),
                id=id_,
                date_text=date,
                desc=desc,
                status=TransactionStatus.get_by_css_class(transaction_class_name),
                amount=value,
                payment_method=payment_method,
                withdrawal_number=recipient
            ))

        user_id = self.tree.xpath('//input[@type="hidden" and @name="user_id"][1]')
        filter_ = self.tree.xpath('//input[@type="hidden" and @name="filter"][1]')
        next_id = self.tree.xpath('//input[@type="hidden" and @name="continue"][1]')

        return TransactionPreviewsBatch(
            raw_source=self.raw_source,
            transactions=result,
            user_id = int(user_id[0].get('value')) if user_id else None,
            filter = filter_[0].get('value') if filter_ else None,
            next_transaction_id= int(next_id[0].get('value')) if next_id else None
        )
