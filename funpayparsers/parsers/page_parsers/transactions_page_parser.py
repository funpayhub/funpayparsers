__all__ = ('TransactionsPageParsingOptions', 'TransactionsPageParser')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.parsers.transaction_previews_parser import (TransactionPreviewsParser,
                                                               TransactionPreviewsParsingOptions)
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParsingOptions, MoneyValueParsingMode
from funpayparsers.parsers.page_header_parser import PageHeaderParser, PageHeaderParsingOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.types.enums import Currency
from funpayparsers.types.pages import TransactionsPage


@dataclass(frozen=True)
class TransactionsPageParsingOptions(ParsingOptions):
    """Options class for ``TransactionsPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``TransactionsPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``TransactionsPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    transaction_previews_parsing_options: TransactionPreviewsParsingOptions = (
        TransactionPreviewsParsingOptions())
    """
    Options instance for ``TransactionPreviewsParser``, which is used by 
    ``TransactionsPageParser``.

    Defaults to ``TransactionPreviewsParsingOptions()``.
    """

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``TransactionsPageParser``.

    Defaults to ``MoneyValueParsingOptions()``.
    """


class TransactionsPageParser(FunPayHTMLObjectParser[TransactionsPage, TransactionsPageParsingOptions]):
    """Class for parsing transactions page (https://funpay.com/account/balance)."""

    def _parse(self):
        header_div = self.tree.css_first('header')
        app_data = self.tree.css_first('body').attributes['data-app-data']

        money_values = []
        for i in self.tree.css('span.balances-value'):
            money_values.append(
                MoneyValueParser(
                    i.html,
                    options=self.options.money_value_parsing_options,
                    parsing_mode=MoneyValueParsingMode.FROM_STRING).parse()
            )

        transactions_div = self.tree.css('div.tc-finance:not([hidden])')
        if not transactions_div:
            transactions = None
        else:
            transactions = TransactionPreviewsParser(
                transactions_div[0].html,
                options=self.options.transaction_previews_parsing_options,
            )

        return TransactionsPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(header_div.html, options=self.options.page_header_parsing_options).parse(),
            app_data=AppDataParser(app_data, self.options.app_data_parsing_options).parse(),
            rub_balance=[i for i in money_values if i.currency is Currency.RUB][0],
            usd_balance=[i for i in money_values if i.currency is Currency.USD][0],
            eur_balance=[i for i in money_values if i.currency is Currency.EUR][0],
            transactions=transactions,
        )
