from funpayparsers.parsers.lot_previews_parser import LotPreviewsParser, LotPreviewsParserOptions
from funpayparsers.types.lots import LotPreview, LotSeller
from funpayparsers.types.common import MoneyValue


OPTIONS = LotPreviewsParserOptions(empty_raw_source=True)


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

common_lot_obj = LotPreview(
    raw_source='',
    id=12345,
    auto_issue=True,
    is_pinned=True,
    desc='Lot Description',
    amount=1,
    price=MoneyValue(
        raw_source='',
        value=3499.796334,
        character='₽'
    ),
    seller=LotSeller(
        raw_source='',
        id=54321,
        username='SellerUsername',
        online=True,
        avatar_url='path/to/avatar',
        register_date_text='на сайте 2 года',
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


def test_common_lot_parsing():
    parser = LotPreviewsParser(common_lot_html, options=OPTIONS)
    assert parser.parse() == [common_lot_obj]