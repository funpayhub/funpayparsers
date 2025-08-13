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
    other_data={
        'user': 54321,
        'without_name': 'some_data_without_name',
        'with_name': 'some_data_with_name',
    },
    other_data_names={
        'with_name': 'Data name'
    }
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
    other_data={
        'server': 97,
    },
    other_data_names={
        'server': 'Эллиан (F2P)'
    }
)


def test_common_lot_parsing():
    parser = OfferPreviewsParser(common_lot_html, options=OPTIONS)
    assert parser.parse() == [common_lot_obj]


def test_currency_lot_parsing():
    parser = OfferPreviewsParser(currency_lot_html, options=OPTIONS)
    assert parser.parse() == [currency_lot_obj]