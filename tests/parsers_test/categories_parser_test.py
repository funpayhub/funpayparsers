from __future__ import annotations

import pytest

from funpayparsers.types import Category, Subcategory, SubcategoryType
from funpayparsers.parsers import CategoriesParser, CategoriesParsingOptions


OPTIONS = CategoriesParsingOptions(empty_raw_source=True)



@pytest.fixture
def single_category_html():
    return """
<div class="promo-game-item">
    <div class="game-title" data-id="344"><a href="https://funpay.com/lots/1407/">Age of Wonders 4</a></div>
    <ul class="list-inline" data-id="344">
        <li><a href="https://funpay.com/lots/1407/">Аккаунты</a></li>
        <li><a href="https://funpay.com/lots/1408/">Ключи</a></li>
    </ul>
</div>
"""


@pytest.fixture
def single_category_obj():
    subcategories = (
        Subcategory(
            raw_source='',
            name='Аккаунты',
            id=1407,
            type=SubcategoryType.COMMON,
            offers_amount=None
        ),
        Subcategory(
            raw_source='',
            name='Ключи',
            id=1408,
            type=SubcategoryType.COMMON,
            offers_amount=None
        )
    )
    return [Category(
        raw_source='',
        id=344,
        name='Age of Wonders 4',
        subcategories=subcategories,
    )]


@pytest.fixture
def multiple_categories_html() -> str:
    return """
<div class="promo-game-item">
    <div class="game-title hidden" data-id="6"><a href="https://funpay.com/chips/6/">Aion</a></div>
    <div class="game-title hidden" data-id="24"><a href="https://funpay.com/chips/26/">Aion</a></div>
    <div class="btn-group btn-group-xs" role="group">
        <button type="button" class="btn btn-gray" data-id="6">RU</button>
        <button type="button" class="btn btn-gray" data-id="24">EU, NA</button>
    </div>
    <ul class="list-inline hidden" data-id="6">
        <li><a href="https://funpay.com/chips/6/">Кинары</a></li>
        <li><a href="https://funpay.com/lots/24/">Аккаунты</a></li>
    </ul>
    <ul class="list-inline hidden" data-id="24">
        <li><a href="https://funpay.com/chips/26/">Кинары2</a></li>
        <li><a href="https://funpay.com/lots/44/">Аккаунты2</a></li>
    </ul>
</div>
"""


@pytest.fixture
def multiple_categories_obj():
    subcategories_1 = (
        Subcategory(
            raw_source='',
            name='Кинары',
            id=6,
            type=SubcategoryType.CURRENCY,
            offers_amount=None
        ),
        Subcategory(
            raw_source='',
            name='Аккаунты',
            id=24,
            type=SubcategoryType.COMMON,
            offers_amount=None
        )
    )

    subcategories_2 = (
        Subcategory(
            raw_source='',
            name='Кинары2',
            id=26,
            type=SubcategoryType.CURRENCY,
            offers_amount=None
        ),
        Subcategory(
            raw_source='',
            name='Аккаунты2',
            id=44,
            type=SubcategoryType.COMMON,
            offers_amount=None
        )
    )

    return [
        Category(
            raw_source='',
            id=6,
            name='Aion',
            subcategories=subcategories_1,
            location='RU'
        ),
        Category(
            raw_source='',
            id=24,
            name='Aion',
            subcategories=subcategories_2,
            location='EU, NA'
        )
    ]


@pytest.mark.parametrize('html,expected',
                         [
                             ('single_category_html', 'single_category_obj'),
                             ('multiple_categories_html', 'multiple_categories_obj')
                         ])
def test_categories_parser(html, expected, request):
    html = request.getfixturevalue(html)
    expected = request.getfixturevalue(expected)
    parser = CategoriesParser(html, options=OPTIONS)
    assert parser.parse() == expected