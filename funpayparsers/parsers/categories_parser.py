from __future__ import annotations


__all__ = ('CategoriesParser', 'CategoriesParsingOptions')

from typing import cast
from dataclasses import dataclass

from selectolax.lexbor import LexborNode

from funpayparsers.types.enums import SubcategoryType
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.categories import Category, Subcategory


@dataclass(frozen=True)
class CategoriesParsingOptions(ParsingOptions):
    """Options class for ``CategoriesParser``."""

    ...


class CategoriesParser(
    FunPayHTMLObjectParser[list[Category], CategoriesParsingOptions],
):
    """
    Class for parsing categories and subcategories.

    Possible locations:
        - Main page (https://funpay.com).
    """

    def _parse(self) -> list[Category]:
        result = []

        for global_cat in self.tree.css('div.promo-game-item'):
            categories = global_cat.css('div.game-title')
            # Some categories have "clones" with different locations (RU, US/EU, etc.)
            # FunPay treats them as different categories,
            # but on main page they are in the same div.
            for cat in categories:
                id_ = int(cast(str, cat.attributes['data-id']))
                locations = global_cat.css(f'button[data-id="{id_}"]')
                location = locations[0].text(strip=True) if locations else None

                result.append(
                    Category(
                        raw_source=global_cat.html or '',
                        id=id_,
                        name=cat.css('a')[0].text(strip=True),
                        location=location,
                        subcategories=self._parse_subcategories(global_cat, id_),
                    )
                )
        return result

    def _parse_subcategories(
        self, global_cat: LexborNode, data_id: int | str
    ) -> tuple[Subcategory, ...]:
        result = []
        div = global_cat.css(f'ul.list-inline[data-id="{data_id}"]')[0]
        for link in div.css('a'):
            url: str = link.attributes['href']  # type: ignore[assignment] # always has href
            result.append(
                Subcategory(
                    raw_source=link.html or '',
                    id=int(url.split('/')[-2]),
                    name=link.text(strip=True),
                    type=SubcategoryType.get_by_url(url),
                    offers_amount=None,
                )
            )

        return tuple(result)
