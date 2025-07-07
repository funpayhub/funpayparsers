__all__ = ('CategoriesParser', 'CategoriesParsingOptions')

from dataclasses import dataclass

from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.types.categories import Category, Subcategory
from funpayparsers.types.enums import SubcategoryType
from selectolax.lexbor import LexborNode


@dataclass(frozen=True)
class CategoriesParsingOptions(ParsingOptions):
    """Options class for ``CategoriesParser``."""
    ...


class CategoriesParser(FunPayHTMLObjectParser[list[Category], CategoriesParsingOptions]):
    """
    Class for parsing categories and subcategories.

    Possible locations:
        - Main page (https://funpay.com).
    """
    def _parse(self):
        result = []

        for global_cat in self.tree.css('div.promo-game-item'):
            categories = global_cat.css('div.game-title')
            # Some categories have "clones" with different locations (RU, US/EU, etc.)
            # FunPay treats them as different categories, but on main page they are in the same div.
            for cat in categories:
                id_ = int(cat.attributes['data-id'])
                location = global_cat.css(f'button[data-id="{id_}"]')
                location = location[0].text(strip=True) if location else None

                result.append(Category(
                    raw_source=global_cat.html,
                    id=id_,
                    name=cat.css('a')[0].text(strip=True),
                    location=location,
                    subcategories=self._parse_subcategories(global_cat, id_),
                ))
        return result

    def _parse_subcategories(self, global_cat: LexborNode,
                             data_id: int | str) -> list[Subcategory]:
        result = []
        div = global_cat.css(f'ul.list-inline[data-id="{data_id}"]')[0]
        for link in div.css('a'):
            result.append(Subcategory(
                raw_source=link.html,
                id=int(link.attributes['href'].split('/')[-2]),
                name=link.text(strip=True),
                type=SubcategoryType.get_by_url(link.attributes['href'])
            ))

        return result
