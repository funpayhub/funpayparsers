__all__ = ('subcategory_data_factory',
           'single_category_html',
           'single_category_obj',
           'multiple_categories_html',
           'multiple_categories_obj',
           'categories_data')

import pytest
from funpayparsers.types import Category, Subcategory, SubcategoryType


@pytest.fixture
def subcategory_data_factory():
    def _factory(*, id: int, name: str, type_: SubcategoryType) -> tuple[str, Subcategory]:
        path = 'lots' if type_ == SubcategoryType.COMMON else 'chips'
        html = f'<li><a href="https://funpay.com/{path}/{id}/">{name}</a></li>'
        obj = Subcategory(
            raw_source='',
            name=name,
            id=id,
            type=type_
        )
        return html, obj
    return _factory


@pytest.fixture
def single_category_html(subcategory_data_factory):
    html1, _ = subcategory_data_factory(id=1, name='Subcategory1Name', type_=SubcategoryType.COMMON)
    html2, _ = subcategory_data_factory(id=2, name='Subcategory2Name', type_=SubcategoryType.CURRENCY)

    return f"""
<div class="promo-game-item">
    <div class="game-title" data-id="123"><a href="https://funpay.com/lots/1/">CategoryName</a></div>
    <ul class="list-inline" data-id="123">
        {html1}
        {html2}
    </ul>
</div>
"""


@pytest.fixture
def single_category_obj(subcategory_data_factory) -> list[Category]:
    _, obj1 = subcategory_data_factory(id=1, name='Subcategory1Name', type_=SubcategoryType.COMMON)
    _, obj2 = subcategory_data_factory(id=2, name='Subcategory2Name', type_=SubcategoryType.CURRENCY)

    return [Category(
        raw_source='',
        id=123,
        name='CategoryName',
        subcategories=[obj1, obj2],
    )]


@pytest.fixture
def multiple_categories_html(subcategory_data_factory) -> str:
    html1, _ = subcategory_data_factory(id=1, name='Subcategory1Name', type_=SubcategoryType.COMMON)
    html2, _ = subcategory_data_factory(id=2, name='Subcategory2Name', type_=SubcategoryType.CURRENCY)
    html3, _ = subcategory_data_factory(id=3, name='Subcategory3Name', type_=SubcategoryType.COMMON)
    html4, _ = subcategory_data_factory(id=4, name='Subcategory4Name', type_=SubcategoryType.CURRENCY)

    return f"""
<div class="promo-game-item">
    <div class="game-title hidden" data-id="123"><a href="https://funpay.com/lots/1/">CategoryName</a></div>
    <div class="game-title hidden" data-id="124"><a href="https://funpay.com/lots/3/">CategoryName</a></div>
    <div class="btn-group btn-group-xs" role="group">
        <button type="button" class="btn btn-gray" data-id="123">Location1</button>
        <button type="button" class="btn btn-gray" data-id="124">Location2</button>
    </div>
    <ul class="list-inline hidden" data-id="123">
        {html1}
        {html2}
    </ul>
    <ul class="list-inline hidden" data-id="124">
        {html3}
        {html4}
    </ul>
</div>
"""


@pytest.fixture
def multiple_categories_obj(subcategory_data_factory):
    _, obj1 = subcategory_data_factory(id=1, name='Subcategory1Name', type_=SubcategoryType.COMMON)
    _, obj2 = subcategory_data_factory(id=2, name='Subcategory2Name', type_=SubcategoryType.CURRENCY)
    _, obj3 = subcategory_data_factory(id=3, name='Subcategory3Name', type_=SubcategoryType.COMMON)
    _, obj4 = subcategory_data_factory(id=4, name='Subcategory4Name', type_=SubcategoryType.CURRENCY)

    return [
        Category(
            raw_source='',
            id=123,
            name='CategoryName',
            subcategories=[obj1, obj2],
            location='Location1'
        ),
        Category(
            raw_source='',
            id=124,
            name='CategoryName',
            subcategories=[obj3, obj4],
            location='Location2'
        )
    ]


@pytest.fixture(
    params=[
        ('single_category_html', 'single_category_obj'),
        ('multiple_categories_html', 'multiple_categories_obj'),
    ],
    ids=['single_category', 'multiple_categories']
)
def categories_data(request) -> tuple[str, Category]:
    html, obj = request.param
    html = request.getfixturevalue(html)
    obj = request.getfixturevalue(obj)
    return html, obj