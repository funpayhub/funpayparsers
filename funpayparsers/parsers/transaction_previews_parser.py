__all__ = ('TransactionPreviewsParser', 'TransactionPreviewsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.types.finances import TransactionPreview
from funpayparsers.types.enums import TransactionStatus, PaymentMethod

from lxml import html


@dataclass(frozen=True)
class TransactionPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class TransactionPreviewsParser(FunPayObjectParser[
    list[TransactionPreview],
    TransactionPreviewsParserOptions
]):

    __options_cls__ = TransactionPreviewsParserOptions

    def _parse(self):
        result = []
        for i in self._tree.xpath('.//div[contains(@class, "tc-item")]'):
            id_ = int(i.get('data-transaction'))
            transaction_class_name = i.get('class').split()[1]  # "tc-item <transaction_class>"

            desc: str = i.xpath('string(.//span[@class="tc-title"][1])')
            date: str = i.xpath('string(.//span[@class="tc-date-time"][1])')

            # Depending on the type of transaction, the recipient's line may or may not be present.
            # The recipient's line exists only in TransactionType.WITHDRAWAL transactions.
            recipient = i.xpath('string(.//span[@class="tc-payment-number"][1])') or None

            payment_method = i.xpath('string(.//span[contains(@class, "payment-logo")][1]/@class)')
            payment_method = None if not payment_method else PaymentMethod.get_by_css_class(payment_method)

            result.append(TransactionPreview(
                raw_source=html.tostring(i, encoding='unicode'),
                id=id_,
                date_text=date,
                desc=desc,
                status=TransactionStatus.get_by_css_class(transaction_class_name),
                amount=...,  # todo
                payment_method=payment_method,
                withdrawal_number=recipient
            ))
        return result
