from __future__ import annotations

from funpayparsers.types.common import MoneyValue
from funpayparsers.types.offers import OfferSeller, OfferPreview
from funpayparsers.parsers.offer_previews_parser import (
    OfferPreviewsParser,
    OfferPreviewsParsingOptions,
)


OPTIONS = OfferPreviewsParsingOptions(empty_raw_source=True)


common_lot_html = """<a href="https://funpay.com/lots/offer?id=12345" class="tc-item offer-promo offer-promoted" 
    data-online="1" data-auto="1" data-user="54321" data-without_name="some_data_without_name" data-with_name="some_data_with_name">
  <div class="tc-desc">
    <div class="tc-desc-text">Lot Description</div>
  </div>
  <div class="tc-with_name hidden-xxs">Data name</div>
  <div class="tc-user">
    <div class="media media-user online style-circle">
      <div class="media-left">
        <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/users/54321/" style="background-image: url(path/to/avatar);"></div>
      </div>
      <div class="media-body">
        <div class="media-user-name">
          <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/users/54321/">SellerUsername</span>
        </div>
        <div class="media-user-reviews">
          <div class="rating-stars rating-5">
            <i class="fas"></i>
            <i class="fas"></i>
            <i class="fas"></i>
            <i class="fas"></i>
            <i class="fas"></i>
          </div>
          <span class="rating-mini-count">105</span>
        </div>
        <div class="media-user-info">на сайте 2 года</div>
      </div>
    </div>
  </div>
  <div class="tc-amount hidden-xxs">1</div>
  <div class="tc-price" data-s="3499.796334">
    <div>3500 <span class="unit">₽</span>
    </div>
    <div class="sc-offer-icons">
      <i class="promo-offer-icon"></i>
    </div>
  </div>
</a>
"""

common_lot_obj = OfferPreview(
    raw_source='',
    id=12345,
    auto_delivery=True,
    is_pinned=True,
    title='Lot Description',
    amount=1,
    price=MoneyValue(
        raw_source='',
        value=3499.796334,
        character='₽'
    ),
    seller=OfferSeller(
        raw_source='',
        id=54321,
        username='SellerUsername',
        online=True,
        avatar_url='path/to/avatar',
        registration_date_text='на сайте 2 года',
        rating=5,
        reviews_amount=105
    ),
    other_data={},
    other_data_names={},
    unit=None
)


currency_lot_html = """
<a href="https://funpay.com/chips/offer?id=15090731-20-20-97-0" class="tc-item" data-server="97">
  <div class="tc-server hidden-xxs">Эллиан (F2P)</div>
  <div class="tc-user">
    <div class="tc-visible-inside visible-xxs">
      <div class="tc-server-inside">Эллиан (F2P)</div>
    </div>
    <div class="media media-user offline style-circle">
      <div class="media-left">
        <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/users/54321/" style="background-image: url(path/to/avatar);"></div>
      </div>
      <div class="media-body">
        <div class="media-user-name">
          <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/users/54321/">SellerUsername</span>
        </div>
        <div class="media-user-reviews">2 отзыва</div>
        <div class="media-user-info">на сайте 2 недели</div>
      </div>
    </div>
  </div>
  <div class="tc-amount" data-s="2000000">2 000 000 <span class="unit">кк</span>
  </div>
  <div class="tc-price" data-s="0">
    <div>0.132 <span class="unit">₽</span>
    </div>
  </div>
</a>
"""

currency_lot_obj = OfferPreview(
    raw_source='',
    id='15090731-20-20-97-0',
    auto_delivery=False,
    is_pinned=False,
    title=None,
    amount=2000000,
    price=MoneyValue(
        raw_source='',
        value=0.132,
        character='₽'
    ),
    seller=OfferSeller(
        raw_source='',
        id=54321,
        username='SellerUsername',
        online=False,
        avatar_url='path/to/avatar',
        registration_date_text='на сайте 2 недели',
        rating=0,
        reviews_amount=2
    ),
    other_data={},
    other_data_names={},
    unit='кк'
)


def test_common_lot_parsing():
    parser = OfferPreviewsParser(common_lot_html, options=OPTIONS)
    assert parser.parse() == [common_lot_obj]


def test_currency_lot_parsing():
    parser = OfferPreviewsParser(currency_lot_html, options=OPTIONS)
    assert parser.parse() == [currency_lot_obj]


# ---------------------------------------------------------------------------
# data-f-* key normalisation (breaking change: f-arena → arena)
# ---------------------------------------------------------------------------

_field_lot_html = """
<a href="https://funpay.com/lots/offer?id=99999" class="tc-item"
   data-online="1" data-f-arena="15" data-f-level="29" data-f-namechange="Есть">
  <div class="tc-desc">
    <div class="tc-desc-text">Крутой аккаунт, 15 арена, 29 уровень, Есть</div>
  </div>
  <div class="tc-user">
    <div class="media media-user online style-circle">
      <div class="media-left">
        <div class="avatar-photo pseudo-a" data-href="https://funpay.com/users/1/" style="background-image: url(a);"></div>
      </div>
      <div class="media-body">
        <div class="media-user-name"><span>Seller</span></div>
        <div class="media-user-reviews">0 отзывов</div>
        <div class="media-user-info">на сайте 1 день</div>
      </div>
    </div>
  </div>
  <div class="tc-price" data-s="1000.0">
    <div>1000 <span class="unit">₽</span></div>
  </div>
</a>
"""


def test_data_f_key_normalization():
    """data-f-arena should be stored as key 'arena', not 'f-arena' (requires structure)."""
    struct = _make_structure()
    opts = OfferPreviewsParsingOptions(empty_raw_source=True, subcategory_structure=struct)
    result = OfferPreviewsParser(_field_lot_html, options=opts).parse()
    assert len(result) == 1
    preview = result[0]
    assert 'arena' in preview.other_data
    assert 'f-arena' not in preview.other_data
    assert preview.other_data['arena'] == 15
    assert preview.other_data['level'] == 29
    assert preview.other_data['namechange'] == 'Есть'


# ---------------------------------------------------------------------------
# Case A: catalog page — enrich other_data_names from structure
# ---------------------------------------------------------------------------

def _make_structure() -> 'SubcategoryStructure':
    from funpayparsers.types.enums import SubcategoryFieldType
    from funpayparsers.types.subcategory_structure import SubcategoryFieldDef, SubcategoryStructure

    fields = [
        SubcategoryFieldDef(raw_source='', id='arena', type=SubcategoryFieldType.NUMERIC_RANGE, label='Арена', conditions=[], options=None),
        SubcategoryFieldDef(raw_source='', id='level', type=SubcategoryFieldType.NUMERIC_RANGE, label='Уровень', conditions=[], options=None),
        SubcategoryFieldDef(raw_source='', id='namechange', type=SubcategoryFieldType.DROPDOWN, label='Изменение имени', conditions=[], options=['Есть', 'Нет']),
    ]
    return SubcategoryStructure(
        subcategory_id=149,
        fields=fields,
        field_map={f.id: f for f in fields},
        label_map={f.label: f.id for f in fields},
    )


def test_case_a_names_enriched_from_structure():
    """With structure on catalog page (data-f-* present), other_data_names is populated."""
    from funpayparsers.parsers.offer_previews_parser import OfferPreviewsParsingOptions

    struct = _make_structure()
    opts = OfferPreviewsParsingOptions(empty_raw_source=True, subcategory_structure=struct)
    result = OfferPreviewsParser(_field_lot_html, options=opts).parse()
    assert len(result) == 1
    preview = result[0]
    assert preview.other_data_names.get('arena') == 'Арена'
    assert preview.other_data_names.get('level') == 'Уровень'
    assert preview.other_data_names.get('namechange') == 'Изменение имени'


# ---------------------------------------------------------------------------
# Case B: profile page — extract field values from title suffix
# ---------------------------------------------------------------------------

_profile_lot_html = """
<a href="https://funpay.com/lots/offer?id=77777" class="tc-item">
  <div class="tc-desc">
    <div class="tc-desc-text">Крутой аккаунт, 15 арена, 29 уровень, Есть</div>
  </div>
  <div class="tc-price" data-s="1000.0">
    <div>1000 <span class="unit">₽</span></div>
  </div>
</a>
"""


def test_case_b_title_fields_extracted():
    """Without data-f-* but with structure, field values are parsed from title suffix."""
    from funpayparsers.parsers.offer_previews_parser import OfferPreviewsParsingOptions

    struct = _make_structure()
    opts = OfferPreviewsParsingOptions(empty_raw_source=True, subcategory_structure=struct)
    result = OfferPreviewsParser(_profile_lot_html, options=opts).parse()
    assert len(result) == 1
    preview = result[0]
    assert preview.other_data.get('arena') == 15
    assert preview.other_data.get('level') == 29
    assert preview.other_data.get('namechange') == 'Есть'
    assert preview.other_data_names.get('arena') == 'Арена'


def test_no_structure_yields_empty_data():
    """Without structure, other_data and other_data_names are always empty."""
    for html in (_profile_lot_html, _field_lot_html):
        result = OfferPreviewsParser(html, options=OPTIONS).parse()
        assert len(result) == 1
        assert result[0].other_data == {}
        assert result[0].other_data_names == {}