from __future__ import annotations


__all__ = ('PageHeaderParsingOptions', 'PageHeaderParser')

from dataclasses import dataclass

from selectolax.lexbor import LexborNode

from funpayparsers.types.enums import Currency, Language
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.utils import parse_money_value_string
from funpayparsers.types.common_page_elements import PageHeader


_CURRENCIES = {
    'rub': Currency.RUB,
    'рубли': Currency.RUB,
    'рублі': Currency.RUB,
    'usd': Currency.USD,
    'доллары': Currency.USD,
    'долари': Currency.USD,
    'eur': Currency.EUR,
    'евро': Currency.EUR,
    'євро': Currency.EUR,
}


@dataclass(frozen=True)
class PageHeaderParsingOptions(ParsingOptions):
    """Options class for ``PageHeaderParser``."""

    ...


class PageHeaderParser(FunPayHTMLObjectParser[PageHeader, PageHeaderParsingOptions]):
    """
    Class for parsing page header.

    Possible locations:
        - Any FunPay page.
    """

    def _parse(self) -> PageHeader:
        header = self.tree.css('header')[0]

        user_dropdown = header.css('a.dropdown-toggle.user-link')
        if user_dropdown:
            return self._parse_authorized_header(header)
        return self._parse_anonymous_header(header)

    def _parse_authorized_header(self, header: LexborNode) -> PageHeader:
        purchases_div = header.css('a.menu-item-orders > span.badge')
        sales_div = header.css('a.menu-item-trade > span.badge')
        chats_div = header.css('a.menu-item-chat > span.badge')
        balance_div = header.css('a.menu-item-balance > span.badge')

        if balance_div:
            money_value = parse_money_value_string(balance_div[0].text().strip())
        else:
            money_value = None

        if money_value is not None:
            currency = money_value.currency
        else:
            currency_text = (
                header.css('a.dropdown-toggle.menu-item-currencies')[0]
                .text(deep=False)
                .strip()
                .lower()
            )

            currency = _CURRENCIES.get(currency_text, Currency.UNKNOWN)
            money_value = MoneyValue(
                raw_source='',
                value=0.0,
                character=currency.value,
            )

        language_class: str = header.css(
            'a.dropdown-toggle.menu-item-langs > i.menu-icon',
        )[0].attributes['class']  # type: ignore[assignment] # always has a class

        logout_button = header.css('a.menu-item-logout')

        return PageHeader(
            raw_source=header.html or '',
            user_id=int(
                header.css('a.user-link-dropdown')[0].attributes['href'].split('/')[-2],  # type: ignore[union-attr] # always has href
            ),
            username=header.css('div.user-link-name')[0].text().strip(),
            avatar_url=header.css('img')[0].attributes['src'],
            language=Language.get_by_header_menu_css_class(language_class),
            currency=currency,
            purchases=int(purchases_div[0].text().strip()) if purchases_div else None,
            sales=int(sales_div[0].text().strip()) if sales_div else None,
            chats=int(chats_div[0].text().strip()) if chats_div else None,
            balance=money_value,
            sales_available=bool(sales_div),
            logout_token=None
            if not logout_button
            else logout_button[0].attributes['href'].split('=')[1],
        )

    def _parse_anonymous_header(self, header: LexborNode) -> PageHeader:
        currency_text = (
            header.css('a.dropdown-toggle.menu-item-currencies')[0]
            .text(deep=False)
            .strip()
            .lower()
        )
        currency = _CURRENCIES.get(currency_text, Currency.UNKNOWN)

        language_class: str = header.css('a.dropdown-toggle.menu-item-langs > i.menu-icon')[
            0
        ].attributes['class']  # type: ignore[assignment] # always has a class

        return PageHeader(
            raw_source=header.html or '',
            user_id=None,
            username=None,
            avatar_url=None,
            language=Language.get_by_header_menu_css_class(language_class),
            currency=currency,
            purchases=None,
            sales=None,
            chats=None,
            balance=None,
            sales_available=False,
            logout_token=None,
        )
