from __future__ import annotations

from funpayparsers.parsers.page_parsers.my_offers_page_parser import MyOffersPageParser


# Minimal but valid anonymous header (currency + language menus),
# like the one a real authenticated trade page always renders.
HEADER = (
    '<header>'
    '<a class="dropdown-toggle menu-item-currencies">rub</a>'
    '<a class="dropdown-toggle menu-item-langs"><i class="menu-icon menu-icon-lang-ru"></i></a>'
    '</header>'
)


def _page(body_inner: str) -> str:
    return (
        '<html><head>'
        '<link rel="alternate" href="https://funpay.com/lots/1452/trade">'
        '</head>'
        f'<body data-app-data=\'{{"locale":"ru","csrf-token":"tok","userId":123}}\'>'
        f'{HEADER}{body_inner}</body></html>'
    )


def test_empty_subcategory_does_not_raise():
    # Regression: when the seller has no offers in a subcategory, FunPay renders
    # the `/lots/<id>/trade` page WITHOUT `div.showcase-table` (and without the
    # `js-lot-raise` button). The parser must treat this as zero offers instead
    # of crashing on `table.html`.
    html = _page('<div class="content-lots"><a href="/lots/1452/trade">Back</a></div>')

    page = MyOffersPageParser(html).parse()

    assert page.offers == {}
    assert page.subcategory_id == 1452
    assert page.category_id is None


def test_subcategory_with_offers():
    html = _page(
        '<div class="content-lots">'
        '<button class="js-lot-raise" data-game="41"></button>'
        '<div class="showcase-table">'
        '<a href="https://funpay.com/lots/offer?id=777" class="tc-item">'
        '<div class="tc-desc"><div class="tc-desc-text">Test offer</div></div>'
        '<div class="tc-price" data-s="100">100 <span class="unit">₽</span></div>'
        '</a>'
        '</div>'
        '</div>'
    )

    page = MyOffersPageParser(html).parse()

    assert page.subcategory_id == 1452
    assert page.category_id == 41
    assert list(page.offers) == [777]
    assert page.offers[777].title == 'Test offer'


def test_non_trade_page_yields_empty_page():
    # Defensive: an unexpected page (e.g. login/redirect) without a header,
    # app-data or `div.content-lots` must not raise.
    page = MyOffersPageParser('<html><body><div>login required</div></body></html>').parse()

    assert page.offers == {}
    assert page.subcategory_id == 0
    assert page.category_id is None
    assert page.header.user_id is None
