from __future__ import annotations


__all__ = ('OfferPageParsingOptions', 'OfferPageParser')

from dataclasses import dataclass

from funpayparsers.parsers import ChatParsingOptions, ChatParser
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParsingOptions, MoneyValueParsingMode
from funpayparsers.types.pages.offer_page import OfferPage
from funpayparsers.types.common import PaymentOption, DetailedUserBalance
from selectolax.lexbor import LexborNode, LexborHTMLParser


@dataclass(frozen=True)
class OfferPageParsingOptions(ParsingOptions):
    """Options class for ``MyOffersPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options for ``PageHeaderParser``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options for ``AppDataParser``.
    """

    chat_parsing_options: ChatParsingOptions = ChatParsingOptions()
    """
    Options for ``ChatParser``.
    """

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions(
        parsing_mode=MoneyValueParsingMode.FROM_STRING
    )
    """
    Options for ``MoneyValueParser``.
    """

class OfferPageParser(FunPayHTMLObjectParser[OfferPage, OfferPageParsingOptions]):
    """
    Parser for offer page (`/<lots/chips>/offer?id=<id>`).
    """

    def _parse(self) -> OfferPage:
        page_content: LexborNode = self.tree.css_first('div.page-content')
        param_list: LexborNode = page_content.css_first('div.param-list')
        auto_delivery: list[LexborNode] = page_content.css('i.auto-dlv-icon')

        fields = {}
        field_divs: list[LexborNode] = param_list.css('div.param-item')
        for field in field_divs:
            name: LexborNode = field.css_first('h5')
            value: LexborNode = field.css('div')[-1]
            fields[name.text(strip=True)] = value.text(strip=True)

        payment_options: dict[str, PaymentOption] = {}
        payment_select: LexborNode = page_content.css_first('select.form-control[name="method"]')
        options: list[LexborNode] = payment_select.css('option')
        for option in options:
            if option.attributes.get('class', None) == 'hidden':
                continue
            tree = LexborHTMLParser(option.attributes['data-content'])
            payment_method_id = 'payment-method-' + option.attributes['value']
            payment_options[payment_method_id] = PaymentOption(
                raw_source=option.html,
                id=payment_method_id,
                title=tree.css_first('span.payment-title').text(strip=True),
                price=MoneyValueParser(
                    raw_source=tree.css_first('span.payment-value').text(strip=True),
                    options=self.options.money_value_parsing_options
                ).parse(),
                factors=[float(i) for i in option.attributes['data-factors'].split(',')],
            )


        return OfferPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                self.tree.css_first('header').html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                self.tree.css_first('body').attributes.get('data-app-data') or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            subcategory_full_name=page_content.css_first('h1').text(strip=True),
            auto_delivery=bool(auto_delivery),
            fields=fields,
            chat=ChatParser(
                self.tree.css_first('div.chat').html or '',
                options=self.options.chat_parsing_options
            ).parse(),
            payment_options=payment_options,
            user_balance=DetailedUserBalance(
                raw_source=payment_select.html,
                total_rub=float(payment_select.attributes['data-balance-total-rub']),
                withdrawable_rub=float(payment_select.attributes['data-balance-rub']),
                total_usd=float(payment_select.attributes['data-balance-total-usd']),
                withdrawable_usd=float(payment_select.attributes['data-balance-usd']),
                total_eur=float(payment_select.attributes['data-balance-total-eur']),
                withdrawable_eur=float(payment_select.attributes['data-balance-eur']),
            )
        )
