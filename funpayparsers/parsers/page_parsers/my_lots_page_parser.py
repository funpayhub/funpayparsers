from __future__ import annotations


__all__ = ('MyLotsPageParsingOptions', 'MyLotsPageParser')

from typing import Any, cast
from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferPreview
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.types.pages.my_lots_page import MyLotsPage
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
class MyLotsPageParsingOptions(ParsingOptions):
    """Options class for ``MyLotsPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options for ``PageHeaderParser``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options for ``AppDataParser``.
    """

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options for ``MoneyValueParser``.
    """


class MyLotsPageParser(FunPayHTMLObjectParser[MyLotsPage, MyLotsPageParsingOptions]):
    """
    Parser for personal lots page (`/lots/<subcategory_id>/trade`).
    """

    def _parse(self) -> MyLotsPage:
        header = PageHeaderParser(
            self.tree.css_first('header').html or '',
            options=self.options.page_header_parsing_options,
        ).parse()

        app_data = AppDataParser(
            self.tree.css_first('body').attributes.get('data-app-data') or '',
            options=self.options.app_data_parsing_options,
        ).parse()

        # subcategory from alternate link: https://funpay.com/lots/<id>/trade
        alt_links = self.tree.css('link[rel="alternate"]')
        subcategory_id = None
        for link in alt_links:
            href = cast(str, link.attributes.get('href', ''))
            if '/lots/' in href and '/trade' in href:
                subcategory_id = int(href.split('/')[-2])
                break

        content = self.tree.css_first('div.content-lots')
        table = content.css_first('div.showcase-table')

        raise_btn = content.css_first('button.js-lot-raise', strict=False)
        game_id = None
        if raise_btn:
            game_str = raise_btn.attributes.get('data-game')
            game_id = int(game_str) if game_str and game_str.isnumeric() else None

        offers: dict[int | str, OfferPreview] = {}
        for item in table.css('a.tc-item'):
            offers[self._parse_offer_id(item)] = self._parse_offer(item)

        return MyLotsPage(
            raw_source=self.raw_source,
            header=header,
            app_data=app_data,
            subcategory_id=subcategory_id if subcategory_id is not None else 0,
            game_id=game_id,
            offers=offers,
        )

    def _parse_offer_id(self, node: Any) -> int | str:
        offer_id = node.attributes.get('data-offer') or ''
        return int(offer_id) if str(offer_id).isnumeric() else offer_id

    def _parse_offer(self, node: Any) -> OfferPreview:
        title_div = node.css_first('div.tc-desc-text', strict=False)
        amount_div = node.css_first('div.tc-amount', strict=False)
        price_div = node.css_first('div.tc-price', strict=False)

        price = MoneyValueParser(
            raw_source=price_div.html or '',
            options=self.options.money_value_parsing_options,
            parsing_mode=MoneyValueParsingMode.FROM_OFFER_PREVIEW,
            parse_value_from_attribute=True,
        ).parse()

        classes = node.attributes.get('class', '')
        return OfferPreview(
            raw_source=node.html or '',
            id=self._parse_offer_id(node),
            auto_delivery=bool(node.css('i.auto-dlv-icon')),
            is_pinned=False,
            title=title_div.text(strip=True) if title_div else None,
            amount=int(amount_div.text(strip=True).replace(' ', '')) if amount_div else None,
            price=price,
            seller=None,
            other_data={},
            other_data_names={},
            disabled='warning' in classes,
        )
