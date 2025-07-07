__all__ = ('PageHeaderParsingOptions', 'PageHeaderParser')

from dataclasses import dataclass
from selectolax.lexbor import LexborNode
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.types.common_page_elements import PageHeader
from funpayparsers.parsers.utils import parse_money_value_string
from funpayparsers.types.enums import Currency, Language
from funpayparsers.types.common import MoneyValue


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

_LANGUAGES = {
    'menu-icon-lang-uk': Language.UK,
    'menu-icon-lang-en': Language.EN,
    'menu-icon-lang-ru': Language.RU
}


@dataclass(frozen=True)
class PageHeaderParsingOptions(ParsingOptions):
    ...


class PageHeaderParser(FunPayHTMLObjectParser[PageHeader, PageHeaderParsingOptions]):
    """
    Class for parsing page header.
    """

    def _parse(self):
        header = self.tree.css('header')[0]

        user_dropdown = header.css('a.dropdown-toggle.user-link')
        if user_dropdown:
            return self._parse_authorized_header(header, user_dropdown[0])
        else:
            return self._parse_anonymous_header(header)

    def _parse_authorized_header(self, header: LexborNode, user_dropdown: LexborNode) -> PageHeader:
        purchases_div = header.css('a.menu-item-orders > span.badge')
        sales_div = header.css('a.menu-item-trade > span.badge')
        chats_div = header.css('a.menu-item-chat > span.badge')
        balance_div = header.css('a.menu-item-balance > span.badge')

        money_value = parse_money_value_string(balance_div[0].text().strip()) if balance_div else None
        if money_value is not None:
            currency = money_value.currency
        else:
            currency_text = header.css('a.dropdown-toggle.menu-item-currencies')[0].text(deep=False).strip().lower()
            currency = _CURRENCIES.get(currency_text, Currency.UNKNOWN)
            money_value = MoneyValue(raw_source='', value=0.0, character=currency.value())

        language_class = header.css('a.dropdown-toggle.menu-item-langs > i.menu-icon')[0].attributes['class']
        for i in _LANGUAGES:
            if i in language_class:
                language = _LANGUAGES[i]
                break
        else:
            language = Language.UNKNOWN


        return PageHeader(
            raw_source=header.html,
            user_id=int(header.css('a.user-link-dropdown')[0].attributes['href'].split('/')[-2]),
            username=header.css('div.user-link-name')[0].text().strip(),
            avatar_url=header.css('img')[0].attributes['src'],
            language=language,
            currency=currency,
            purchases=int(purchases_div[0].text().strip()) if purchases_div else None,
            sales=int(sales_div[0].text().strip()) if sales_div else None,
            chats=int(chats_div[0].text().strip()) if chats_div else None,
            balance=money_value
        )

    def _parse_anonymous_header(self, header: LexborNode) -> PageHeader:
        currency_text = header.css('a.dropdown-toggle.menu-item-currencies')[0].text(deep=False).strip().lower()
        currency = _CURRENCIES.get(currency_text, Currency.UNKNOWN)

        language_class = header.css('a.dropdown-toggle.menu-item-langs > i.menu-icon')[0].attributes['class']
        for i in _LANGUAGES:
            if i in language_class:
                language = _LANGUAGES[i]
                break
        else:
            language = Language.UNKNOWN

        return PageHeader(
            raw_source=header.html,
            user_id=None,
            username=None,
            avatar_url=None,
            language=language,
            currency=currency,
            purchases=None,
            sales=None,
            chats=None,
            balance=None
        )
