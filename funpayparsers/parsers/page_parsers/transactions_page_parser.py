from __future__ import annotations


__all__ = ('TransactionsPageParsingOptions', 'TransactionsPageParser')

from dataclasses import dataclass

from funpayparsers.types.enums import Currency
from funpayparsers.types.pages import TransactionsPage
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.parsers.transaction_previews_parser import (
    TransactionPreviewsParser,
    TransactionPreviewsParsingOptions,
)


@dataclass(frozen=True)
class TransactionsPageParsingOptions(ParsingOptions):
    """Options class for ``TransactionsPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, 
    which is used by ``TransactionsPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``TransactionsPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    transaction_previews_parsing_options: TransactionPreviewsParsingOptions = (
        TransactionPreviewsParsingOptions()
    )
    """
    Options instance for ``TransactionPreviewsParser``, which is used by 
    ``TransactionsPageParser``.

    Defaults to ``TransactionPreviewsParsingOptions()``.
    """

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, 
    which is used by ``TransactionsPageParser``.
    
    ``parsing_mode`` option is hardcoded in ``TransactionsPageParser`` 
    and is therefore ignored if provided externally.

    Defaults to ``MoneyValueParsingOptions()``.
    """


class TransactionsPageParser(
    FunPayHTMLObjectParser[TransactionsPage, TransactionsPageParsingOptions],
):
    """Class for parsing the transactions page (https://funpay.com/account/balance)."""

    def _parse(self) -> TransactionsPage:
        money_values = []
        for i in self.tree.css('span.balances-value'):
            money_values.append(
                MoneyValueParser(
                    i.text().strip(),
                    options=self.options.money_value_parsing_options,
                    parsing_mode=MoneyValueParsingMode.FROM_STRING,
                ).parse(),
            )
            if len(money_values) == 3:
                break

        rub_balance = [i for i in money_values if i.currency is Currency.RUB]
        usd_balance = [i for i in money_values if i.currency is Currency.USD]
        eur_balance = [i for i in money_values if i.currency is Currency.EUR]

        transactions_div = self.tree.css('div.tc-finance:not(.hidden)')
        if not transactions_div:
            transactions = None
        else:
            transactions = TransactionPreviewsParser(
                transactions_div[0].html or '',
                options=self.options.transaction_previews_parsing_options,
            ).parse()

        return TransactionsPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                self.tree.css_first('header').html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                self.tree.css_first('body').attributes['data-app-data'] or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            rub_balance=rub_balance[0] if rub_balance else None,
            usd_balance=usd_balance[0] if usd_balance else None,
            eur_balance=eur_balance[0] if eur_balance else None,
            transactions=transactions,
        )
