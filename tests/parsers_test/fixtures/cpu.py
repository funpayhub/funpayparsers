__all__ = ('currently_viewing_offer_info_html', 'currently_viewing_offer_info_obj')

from funpayparsers.types import CurrentlyViewingOfferInfo
import pytest


@pytest.fixture
def currently_viewing_offer_info_html() -> str:
    return """<h5>Покупатель смотрит</h5>
<div>
  <a href="https://funpay.com/chips/offer?id=123456-789-10-11-12">Lot name</a>
</div>"""


@pytest.fixture
def currently_viewing_offer_info_obj() -> CurrentlyViewingOfferInfo:
    return CurrentlyViewingOfferInfo(
        raw_source='',
        id='123456-789-10-11-12',
        name='Lot name'
    )
