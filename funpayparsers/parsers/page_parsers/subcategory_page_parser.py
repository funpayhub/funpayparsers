from __future__ import annotations


__all__ = ('SubcategoryPageParsingOptions', 'SubcategoryPageParser')

from dataclasses import dataclass

from funpayparsers.types.enums import SubcategoryType
from funpayparsers.types.pages import SubcategoryPage
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.categories import Subcategory
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.parsers.offer_previews_parser import (
    OfferPreviewsParser,
    OfferPreviewsParsingOptions,
)


@dataclass(frozen=True)
class SubcategoryPageParsingOptions(ParsingOptions):
    """Options class for ``SubcategoryPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, 
    which is used by ``SubcategoryPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``SubcategoryPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    offer_previews_parsing_options: OfferPreviewsParsingOptions = OfferPreviewsParsingOptions()
    """
    Options instance for ``OfferPreviewsParser``, 
    which is used by ``SubcategoryPageParser``.

    Defaults to ``OfferPreviewsParsingOptions()``.
    """


class SubcategoryPageParser(
    FunPayHTMLObjectParser[
        SubcategoryPage,
        SubcategoryPageParsingOptions,
    ]
):
    """
    Class for parsing subcategory offer list pages
    (`https://funpay.com/<lots/chips>/<subcategory_id>/`).
    """

    def _parse(self) -> SubcategoryPage:
        showcase = self.tree.css_first('div.showcase')

        # lot-ID / chips-ID
        subcategory_id_str: str = showcase.attributes['data-section']  # type: ignore[assignment]
        # always has 'data-section'
        related_subcategories = []
        subcategory_type = SubcategoryType.get_by_showcase_data_section(subcategory_id_str)

        for i in self.tree.css('a.counter-item'):
            url: str = i.attributes['href']  # type: ignore[assignment]
            # 'a' always has 'href'.
            related_subcategories.append(
                Subcategory(
                    raw_source=i.html or '',
                    id=int(url.split('/')[-2]),
                    type=subcategory_type,
                    name=i.css_first('div.counter-param').text().strip(),
                    offers_amount=int(i.css_first('div.counter-value').text().strip()),
                )
            )

        return SubcategoryPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                self.tree.css_first('header').html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                self.tree.css_first('body').attributes['data-app-data'] or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            category_id=int(
                showcase.attributes['data-game']  # type: ignore[arg-type] # always has data-game
            ),
            subcategory_id=int(subcategory_id_str.split('-')[-1]),
            subcategory_type=subcategory_type,
            related_subcategories=related_subcategories or None,
            offers=OfferPreviewsParser(
                showcase.html or '',
                options=self.options.offer_previews_parsing_options,
            ).parse()
            or None,
        )
