from __future__ import annotations


__all__ = ('MyOffersPageParsingOptions', 'MyOffersPageParser')

from typing import cast
from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.types.pages.my_offers_page import MyOffersPage
from funpayparsers.parsers.offer_previews_parser import (
    OfferPreviewsParser,
    OfferPreviewsParsingOptions,
)


@dataclass(frozen=True)
class MyOffersPageParsingOptions(ParsingOptions):
    """Options class for ``MyOffersPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options for ``PageHeaderParser``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options for ``AppDataParser``.
    """

    offer_previews_parsing_options: OfferPreviewsParsingOptions = OfferPreviewsParsingOptions()
    """
    Options for ``OfferPreviewsParser``.
    """


class MyOffersPageParser(FunPayHTMLObjectParser[MyOffersPage, MyOffersPageParsingOptions]):
    """
    Parser for personal lots page (`/lots/<subcategory_id>/trade`).
    """

    def _parse(self) -> MyOffersPage:
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
        category_id = None
        if raise_btn:
            game_str = raise_btn.attributes.get('data-game')
            category_id = int(game_str) if game_str and game_str.isnumeric() else None

        return MyOffersPage(
            raw_source=self.raw_source,
            header=header,
            app_data=app_data,
            subcategory_id=subcategory_id if subcategory_id is not None else 0,
            category_id=category_id,
            offers={
                offer_preview.id: offer_preview
                for offer_preview in OfferPreviewsParser(
                    raw_source=table.html or '',
                    options=self.options.offer_previews_parsing_options,
                ).parse()
            },
        )
