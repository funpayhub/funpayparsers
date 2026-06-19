from __future__ import annotations

from funpayparsers.parsers.page_parsers.my_chips_page_parser import MyChipsPageParser


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
        '<link rel="alternate" href="https://funpay.com/chips/210/trade">'
        '</head>'
        f'<body data-app-data=\'{{"locale":"ru","csrf-token":"tok","userId":123}}\'>'
        f'{HEADER}{body_inner}</body></html>'
    )


def test_empty_subcategory_does_not_raise():
    # Regression: when the seller has no chips offers, FunPay renders the
    # `/chips/<id>/trade` page WITHOUT `form.form-ajax-simple`. The parser must
    # treat this as empty fields instead of crashing on `form.html`.
    page = MyChipsPageParser(_page('<div class="content">no chips</div>')).parse()

    assert page.subcategory_id == 210
    assert page.fields.fields_dict == {}
    assert page.category_id is None


def test_subcategory_with_chips():
    # Regression: `OfferFieldsParser` historically looked only for
    # `div.page-content > form`, while this parser feeds it the bare `<form>`
    # HTML. Non-empty chips subcategories must now parse the fields correctly.
    chips_form = (
        '<div class="page-content">'
        '<form class="form-ajax-simple" method="post">'
        '<input type="hidden" name="game" value="41">'
        '<input type="hidden" name="csrf_token" value="x">'
        '<input type="text" name="chip" value="gold">'
        '</form>'
        '</div>'
    )

    page = MyChipsPageParser(_page(chips_form)).parse()

    assert page.subcategory_id == 210
    assert page.category_id == 41
    assert page.fields.fields_dict == {'game': '41', 'chip': 'gold'}


def test_non_trade_page_yields_empty_page():
    # Defensive: an unexpected page (e.g. login/redirect) without a header,
    # app-data or form must not raise.
    page = MyChipsPageParser('<html><body><div>login required</div></body></html>').parse()

    assert page.subcategory_id == 0
    assert page.category_id is None
    assert page.fields.fields_dict == {}
    assert page.header.user_id is None
