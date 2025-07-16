from __future__ import annotations

import pytest

from funpayparsers.types import PrivateChatInfo, CurrentlyViewingOfferInfo
from funpayparsers.parsers import PrivateChatInfoParser, PrivateChatInfoParsingOptions


OPTIONS = PrivateChatInfoParsingOptions(empty_raw_source=True)


@pytest.fixture
def chat_info_template_html():
    return """
<div class="chat-detail-list custom-scroll">
  <div class="param-item">
    <h5>Дата регистрации</h5>
    <div> 8 декабря 2024, 21:24 <br> 7 месяцев назад </div>
  </div>
  {language_div}
  {cpu_div}
</div>
"""


@pytest.fixture
def language_div_html():
    return """<div class="param-item">
                                <h5>Язык собеседника</h5>
                                <div>Английский</div>
                            </div>"""


@pytest.fixture
def cpu_div_html():
    return """<div class="param-item chat-panel" data-type="c-p-u" data-id="13153966" data-tag="df4t41qr">
                            <h5>Покупатель смотрит</h5>
        <div><a href="https://funpay.com/chips/offer?id=12345-678-90-1">Lot name</a></div>                        </div>"""


@pytest.fixture
def cpu_obj():
    return CurrentlyViewingOfferInfo(
        raw_source='',
        id='12345-678-90-1',
        title='Lot name'
    )


@pytest.fixture
def chat_info_with_language_html(chat_info_template_html, language_div_html, cpu_div_html):
    return chat_info_template_html.format(
        cpu_div='',
        language_div=language_div_html,
    )


@pytest.fixture
def chat_info_with_cpu_html(chat_info_template_html, cpu_div_html):
    return chat_info_template_html.format(
        cpu_div=cpu_div_html,
        language_div=''
    )


@pytest.fixture
def chat_info_full_html(chat_info_template_html, language_div_html, cpu_div_html):
    return chat_info_template_html.format(
        cpu_div=cpu_div_html,
        language_div=language_div_html,
    )


@pytest.fixture
def chat_info_with_language_obj():
    return PrivateChatInfo(
        raw_source='',
        registration_date_text='8 декабря 2024, 21:24',
        language='Английский',
        currently_viewing_offer=None
    )


@pytest.fixture
def chat_info_with_cpu_obj(cpu_obj):
    return PrivateChatInfo(
        raw_source='',
        registration_date_text='8 декабря 2024, 21:24',
        language=None,
        currently_viewing_offer=cpu_obj
    )


@pytest.fixture
def chat_info_full_obj(cpu_obj):
    return PrivateChatInfo(
        raw_source='',
        registration_date_text='8 декабря 2024, 21:24',
        language='Английский',
        currently_viewing_offer = cpu_obj
    )


@pytest.mark.parametrize('html,expected', [
    ('chat_info_with_language_html', 'chat_info_with_language_obj'),
    ('chat_info_with_cpu_html', 'chat_info_with_cpu_obj'),
    ('chat_info_full_html', 'chat_info_full_obj'),
])
def test_private_chat_info_parsing(html, expected, request):
    html = request.getfixturevalue(html)
    expected = request.getfixturevalue(expected)
    parser = PrivateChatInfoParser(html, OPTIONS)
    assert parser.parse() == expected