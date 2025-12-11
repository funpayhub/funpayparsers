from __future__ import annotations


__all__ = ('MyChipsPageParsingOptions', 'MyChipsPageParser')

from typing import cast
from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferFields
from funpayparsers.parsers.utils import serialize_form
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.types.pages.my_chips_page import MyChipsPage
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
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


class MyChipsPageParser(FunPayHTMLObjectParser[MyChipsPage, MyChipsPageParsingOptions]):
    """
    Parser for personal chips page (`/chips/<subcategory_id>/trade`).
    """

    def _parse(self) -> MyChipsPage:
        header = PageHeaderParser(
            self.tree.css_first('header').html or '',
            options=self.options.page_header_parsing_options,
        ).parse()

        app_data = AppDataParser(
            self.tree.css_first('body').attributes.get('data-app-data') or '',
            options=self.options.app_data_parsing_options,
        ).parse()

        form = self.tree.css_first('form.form-ajax-simple')
        fields_dict = serialize_form(form)

        # game id is stored as hidden input "game"
        game_id = None
        game_val = fields_dict.get('game')
        if game_val and str(game_val).isnumeric():
            game_id = int(game_val)

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
            game_id=game_id,
            fields=OfferFields(raw_source=form.html or '', fields_dict=fields_dict),
        )
