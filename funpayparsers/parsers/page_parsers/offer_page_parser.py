from __future__ import annotations


__all__ = ('OfferPageParsingOptions', 'OfferPageParser')

from typing import cast
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
        # Offer pages always include these layout nodes; missing nodes are
        # handled by the base parser wrapper as ParsingError.
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

            # Visible payment options always carry these data attributes.
            data_content = cast(str, option.attributes.get('data-content'))
            payment_method_value = cast(str, option.attributes.get('value'))
            data_factors = cast(str, option.attributes.get('data-factors'))
            tree = LexborHTMLParser(data_content)
            payment_method_id = 'payment-method-' + payment_method_value
            payment_title: LexborNode = tree.css_first('span.payment-title')
            payment_value: LexborNode = tree.css_first('span.payment-value')

            payment_options[payment_method_id] = PaymentOption(
                raw_source=cast(str, option.html),
                id=payment_method_id,
                title=payment_title.text(strip=True),
                price=MoneyValueParser(
                    raw_source=payment_value.text(strip=True),
                    options=self.options.money_value_parsing_options,
                ).parse(),
                factors=[float(i) for i in data_factors.split(',')],
            )

        header_tag: LexborNode = self.tree.css_first('header')
        body_tag: LexborNode = self.tree.css_first('body')
        chat_tag: LexborNode = self.tree.css_first('div.chat')
        subcategory_title: LexborNode = page_content.css_first('h1')

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
                raw_source=cast(str, payment_select.html),
                total_rub=float(
                    cast(str, payment_select.attributes.get('data-balance-total-rub'))
                ),
                withdrawable_rub=float(
                    cast(str, payment_select.attributes.get('data-balance-rub'))
                ),
                total_usd=float(
                    cast(str, payment_select.attributes.get('data-balance-total-usd'))
                ),
                withdrawable_usd=float(
                    cast(str, payment_select.attributes.get('data-balance-usd'))
                ),
                total_eur=float(
                    cast(str, payment_select.attributes.get('data-balance-total-eur'))
                ),
                withdrawable_eur=float(
                    cast(str, payment_select.attributes.get('data-balance-eur'))
                ),
            ),
        )
