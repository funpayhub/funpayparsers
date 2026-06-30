from __future__ import annotations


__all__ = ('SrasInfoPageParser', 'SrasInfoPageParsingOptions')

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from selectolax.lexbor import LexborNode

from funpayparsers.types.sras import SrasSectionRestriction
from funpayparsers.types.enums import SubcategoryType
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.types.pages.sras_info_page import SrasInfoPage


RATING_RE = re.compile(r'(\d+)')


@dataclass(frozen=True)
class SrasInfoPageParsingOptions(ParsingOptions):
    """Options class for ``SrasInfoPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``SrasInfoPageParser``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``SrasInfoPageParser``.
    """


class SrasInfoPageParser(FunPayHTMLObjectParser[SrasInfoPage, SrasInfoPageParsingOptions]):
    """Parser for SRAS info page (`https://funpay.com/sras/info`)."""

    def _parse(self) -> SrasInfoPage:
        header_tag = self.tree.css_first('header')
        body_tag = self.tree.css_first('body')
        content_tag = self.tree.css_first('div.page-content-full')
        if header_tag is None or body_tag is None or content_tag is None:
            raise ValueError('SRAS info page source is missing required layout nodes.')

        restrictions: dict[SubcategoryType, dict[int, SrasSectionRestriction]] = {}

        for row in content_tag.css('table tbody tr'):
            restriction = self._parse_restriction(row)
            by_type = restrictions.setdefault(restriction.subcategory_type, {})
            by_type[restriction.subcategory_id] = restriction

        return SrasInfoPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                header_tag.html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                body_tag.attributes.get('data-app-data') or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            restrictions=restrictions,
        )

    def _parse_restriction(self, row: LexborNode) -> SrasSectionRestriction:
        cells = row.css('td')
        link = cells[0].css_first('a')
        if link is None:
            raise ValueError('SRAS restriction row is missing a subcategory link.')

        href = link.attributes.get('href')
        if href is None:
            raise ValueError('SRAS restriction link is missing href.')

        subcategory_type = SubcategoryType.from_url(href)
        subcategory_id = self._parse_subcategory_id(href)
        max_rating = self._parse_max_rating(cells[1].text(strip=True))

        return SrasSectionRestriction(
            raw_source=row.html or '',
            subcategory_id=subcategory_id,
            subcategory_type=subcategory_type,
            max_rating=max_rating,
        )

    def _parse_subcategory_id(self, href: str) -> int:
        path_parts = [part for part in urlparse(href).path.split('/') if part]
        return int(path_parts[-1])

    def _parse_max_rating(self, text: str) -> int:
        return int(RATING_RE.search(text).group(1))  # type: ignore[union-attr]
