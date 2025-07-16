from __future__ import annotations

from funpayparsers.types.common import CurrentlyViewingOfferInfo
from funpayparsers.parsers.cpu_parser import (
    CurrentlyViewingOfferInfoParser,
    CurrentlyViewingOfferInfoParsingOptions,
)


OPTIONS = CurrentlyViewingOfferInfoParsingOptions(empty_raw_source=True)


cpu_html = """
<h5>Покупатель смотрит</h5>
<div>
  <a href="https://funpay.com/chips/offer?id=123456-789-10-11-12">Lot desc</a>
</div>
"""

cpu_obj = CurrentlyViewingOfferInfo(
    raw_source='',
    id='123456-789-10-11-12',
    title='Lot desc',
)


def test_cpu_parser():
    parser = CurrentlyViewingOfferInfoParser(cpu_html, options=OPTIONS)
    assert parser.parse() == cpu_obj
