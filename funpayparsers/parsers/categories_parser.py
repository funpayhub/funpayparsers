__all__ = ('CategoriesParser', 'CategoriesParserOptions')

from dataclasses import dataclass

from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.types.categories import Category, Subcategory
from funpayparsers.types.enums import SubcategoryType
from lxml import html


@dataclass(frozen=True)
class CategoriesParserOptions(FunPayObjectParserOptions):
    ...


class CategoriesParser(FunPayHTMLObjectParser[list[Category], CategoriesParserOptions]):
    def _parse(self):
        result = []

        for global_cat in self.tree.xpath('//div[contains(@class,"promo-game-item")]'):
            categories = global_cat.xpath('.//div[contains(@class, "game-title")]')
            if len(categories) > 1:
                result.extend(self._parse_multiple_categories(categories, global_cat))
                continue

            cat = categories[0]
            id_ = int(cat.get('data-id'))
            name = cat.xpath('string(.//a[1])')
            subcategories = self._parse_subcategories(global_cat, id_)
            result.append(Category(
                raw_source=html.tostring(global_cat),
                id=id_,
                name=name,
                location=None,
                subcategories=subcategories,
            ))
        return result

    def _parse_multiple_categories(self,
                                   categories: list[html.HtmlElement],
                                   global_cat: html.HtmlElement):
        result = []
        for cat in categories:
            id_ = int(cat.get('data-id'))
            name = cat.xpath('string(.//a[1])')
            location = global_cat.xpath(f'string(.//button[@data-id="{id_}"][1])')
            subcategories = self._parse_subcategories(global_cat, id_)
            result.append(Category(
                raw_source=html.tostring(global_cat, encoding='unicode'),
                id=id_,
                name=name,
                location=location,
                subcategories=subcategories,
            ))
        return result

    def _parse_subcategories(self, global_cat: html.HtmlElement,
                             data_id: int | str) -> list[Subcategory]:
        result = []
        div = global_cat.xpath(f'.//ul[contains(@class, "list-inline") and @data-id="{data_id}"]')[0]
        for link in div.xpath('.//a'):
            id_ = link.get('href').split('/')[-2]
            id_ = int(id_) if id_.isnumeric() else id_
            name = link.xpath('string(.)').strip()

            result.append(Subcategory(
                raw_source=html.tostring(link, encoding='unicode'),
                id=id_,
                name=name,
                type=SubcategoryType.get_by_url(link.get('href'))
            ))

        return result
