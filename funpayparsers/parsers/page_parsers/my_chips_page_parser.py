from __future__ import annotations


__all__ = ('MyChipsPageParsingOptions', 'MyChipsPageParser')

from typing import cast
from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.types.pages.my_chips_page import MyChipsPage
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.parsers.offer_fields_parser import (
    OfferFieldsParser,
    OfferFieldsParsingOptions,
)


@dataclass(frozen=True)
class MyChipsPageParsingOptions(ParsingOptions):
    """Options class for ``MyChipsPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options for ``PageHeaderParser``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options for ``AppDataParser``.
    """

    offer_fields_parsing_options: OfferFieldsParsingOptions = OfferFieldsParsingOptions()
    """
    Options for ``OfferFieldsParser``.
    """


class MyChipsPageParser(FunPayHTMLObjectParser[MyChipsPage, MyChipsPageParsingOptions]):
    """
    Parser for personal chips page (`/chips/<subcategory_id>/trade`).
    """

    def _parse(self) -> MyChipsPage:
        header_node = self.tree.css_first('header')
        header = PageHeaderParser(
            header_node.html or '' if header_node else '',
            options=self.options.page_header_parsing_options,
        ).parse()

        body_node = self.tree.css_first('body')
        app_data_str = body_node.attributes.get('data-app-data') if body_node else None
        app_data = AppDataParser(
            app_data_str or '',
            options=self.options.app_data_parsing_options,
        ).parse()

        # The form is absent when the subcategory has no chips offers (or on
        # non-trade pages). ``OfferFieldsParser`` returns empty fields for an
        # empty source, so no offers parse into an empty ``OfferFields``.
        form = self.tree.css_first('form.form-ajax-simple')
        fields_obj = OfferFieldsParser(
            raw_source=form.html or '' if form else '',
            options=self.options.offer_fields_parsing_options,
        ).parse()

        # game id is stored as hidden input "game"
        category_id = None
        game_val = fields_obj.fields_dict.get('game')
        if game_val and str(game_val).isnumeric():
            category_id = int(game_val)

        # subcategory from alternate link: https://funpay.com/chips/<id>/trade
        subcategory_id = None
        for link in self.tree.css('link[rel="alternate"]'):
            href = cast(str, link.attributes.get('href', ''))
            if '/chips/' in href and '/trade' in href:
                subcategory_id = int(href.split('/')[-2])
                break

        return MyChipsPage(
            raw_source=self.raw_source,
            header=header,
            app_data=app_data,
            subcategory_id=subcategory_id if subcategory_id is not None else 0,
            category_id=category_id,
            fields=fields_obj,
        )
