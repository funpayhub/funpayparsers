from __future__ import annotations


__all__ = ('OfferPageParsingOptions', 'OfferPageParser')

from dataclasses import dataclass

from selectolax.lexbor import LexborNode, LexborHTMLParser

from funpayparsers.parsers import ChatParser, ChatParsingOptions
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import PaymentOption, DetailedUserBalance
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.types.pages.offer_page import OfferPage
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)


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
        if page_content is None:
            raise ValueError('Offer page source is missing page content.')

        param_list: LexborNode = page_content.css_first('div.param-list')
        if param_list is None:
            raise ValueError('Offer page source is missing params list.')

        auto_delivery: list[LexborNode] = page_content.css('i.auto-dlv-icon')

        fields = {}
        field_divs: list[LexborNode] = param_list.css('div.param-item')
        for field in field_divs:
            name: LexborNode = field.css_first('h5')
            if name is None:
                raise ValueError('Offer param item is missing name.')

            value: LexborNode = field.css('div')[-1]
            fields[name.text(strip=True)] = value.text(strip=True)

        payment_options: dict[str, PaymentOption] = {}
        payment_select: LexborNode = page_content.css_first('select.form-control[name="method"]')
        if payment_select is None:
            raise ValueError('Offer page source is missing payment method selector.')

        options: list[LexborNode] = payment_select.css('option')
        for option in options:
            if option.attributes.get('class', None) == 'hidden':
                continue

            data_content = option.attributes.get('data-content')
            payment_method_value = option.attributes.get('value')
            data_factors = option.attributes.get('data-factors')
            if data_content is None or payment_method_value is None or data_factors is None:
                raise ValueError('Payment option is missing required attributes.')

            tree = LexborHTMLParser(data_content)
            payment_method_id = 'payment-method-' + payment_method_value
            payment_title = tree.css_first('span.payment-title')
            payment_value = tree.css_first('span.payment-value')
            if payment_title is None or payment_value is None:
                raise ValueError('Payment option content is missing title or value.')

            payment_options[payment_method_id] = PaymentOption(
                raw_source=option.html or '',
                id=payment_method_id,
                title=payment_title.text(strip=True),
                price=MoneyValueParser(
                    raw_source=payment_value.text(strip=True),
                    options=self.options.money_value_parsing_options,
                ).parse(),
                factors=[float(i) for i in data_factors.split(',')],
            )

        header_tag = self.tree.css_first('header')
        body_tag = self.tree.css_first('body')
        chat_tag = self.tree.css_first('div.chat')
        subcategory_title = page_content.css_first('h1')
        if header_tag is None or body_tag is None or chat_tag is None or subcategory_title is None:
            raise ValueError('Offer page source is missing required layout nodes.')

        balance_total_rub = payment_select.attributes.get('data-balance-total-rub')
        balance_rub = payment_select.attributes.get('data-balance-rub')
        balance_total_usd = payment_select.attributes.get('data-balance-total-usd')
        balance_usd = payment_select.attributes.get('data-balance-usd')
        balance_total_eur = payment_select.attributes.get('data-balance-total-eur')
        balance_eur = payment_select.attributes.get('data-balance-eur')
        if (
            balance_total_rub is None
            or balance_rub is None
            or balance_total_usd is None
            or balance_usd is None
            or balance_total_eur is None
            or balance_eur is None
        ):
            raise ValueError('Payment selector is missing balance attributes.')

        return OfferPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                header_tag.html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                body_tag.attributes.get('data-app-data') or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            subcategory_full_name=subcategory_title.text(strip=True),
            auto_delivery=bool(auto_delivery),
            fields=fields,
            chat=ChatParser(
                chat_tag.html or '',
                options=self.options.chat_parsing_options,
            ).parse(),
            payment_options=payment_options,
            user_balance=DetailedUserBalance(
                raw_source=payment_select.html or '',
                total_rub=float(balance_total_rub),
                withdrawable_rub=float(balance_rub),
                total_usd=float(balance_total_usd),
                withdrawable_usd=float(balance_usd),
                total_eur=float(balance_total_eur),
                withdrawable_eur=float(balance_eur),
            ),
        )
