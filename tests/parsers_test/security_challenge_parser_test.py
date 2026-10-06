from __future__ import annotations

import pytest

from funpayparsers.types.security import SecurityChallengeKind
from funpayparsers.parsers.security_challenge_parser import (
    SecurityChallengeParser,
    SecurityChallengeParsingOptions,
)


OPTIONS = SecurityChallengeParsingOptions(empty_raw_source=True)


TWO_FACTOR_HTML = """
<div id="content" class="security-challenge">
    <h1>Двухфакторная аутентификация</h1>
    <div>
        <form method="post" class="form-ajax-simple">
            <div class="form-group">
                <label>Сгенерированный 6-значный код</label>
                <input type="text" class="form-control" name="twofactor_code"
                       autocomplete="off" inputmode="decimal" placeholder="000 000">
            </div>
            <button type="submit" class="btn btn-primary">Продолжить</button>
        </form>
    </div>
</div>
"""

PHONE_HTML = """
<div id="content" class="security-challenge">
    <h1>Проверка безопасности</h1>
    <div>
        <p>Вы пытаетесь зайти из необычного места.</p>
        <p>Чтобы подтвердить, что вы владелец аккаунта, <strong>укажите последние 4 цифры этого номера</strong>.</p>
        <form method="post" class="form-ajax-simple" action="https://funpay.com/security/ipChallengeCheck">
            <div class="form-group input-group">
                <span class="input-group-addon">Телефон +7***350****</span>
                <input type="text" name="0" class="form-control" placeholder="1234" autocomplete="off">
            </div>
            <button type="submit" class="btn btn-primary">Подтвердить</button>
        </form>
    </div>
</div>
"""


def _parse(html: str):
    return SecurityChallengeParser(html, options=OPTIONS).parse()


@pytest.mark.parametrize(
    ('html', 'kind', 'name', 'length', 'action_path'),
    [
        (TWO_FACTOR_HTML, SecurityChallengeKind.TWO_FACTOR, 'twofactor_code', 6, None),
        (PHONE_HTML, SecurityChallengeKind.PHONE_DIGITS, '0', 4, 'security/ipChallengeCheck'),
    ],
    ids=['two-factor', 'phone-digits'],
)
def test_known_pages_are_recognized_by_their_structure(html, kind, name, length, action_path):
    challenge = _parse(html)
    assert challenge.kind is kind
    assert [f.name for f in challenge.fields] == [name]
    assert challenge.fields[0].length == length
    assert challenge.action_path == action_path


def test_title_hint_and_label_are_read():
    challenge = _parse(PHONE_HTML)
    assert challenge.title == 'Проверка безопасности'
    assert 'необычного места' in challenge.hint
    assert challenge.fields[0].label == 'Телефон +7***350****'


def test_a_form_nobody_has_seen_is_unknown_but_has_answer_slots():
    card = PHONE_HTML.replace('Телефон +7***350****', 'Карта 4276********')
    challenge = _parse(card)
    assert challenge.kind is SecurityChallengeKind.UNKNOWN
    assert challenge.form_data(' 1 234 ') == {'0': '1234'}
    with pytest.raises(ValueError, match='1 field'):
        challenge.form_data('1', '2')


def test_shape_hash_ignores_the_phone_but_tells_phone_from_card():
    phone = _parse(PHONE_HTML)
    other_phone = _parse(PHONE_HTML.replace('+7***350****', '+7***911****'))
    card = _parse(PHONE_HTML.replace('Телефон +7***350****', 'Карта 4276********'))
    assert phone.shape_hash == other_phone.shape_hash
    assert phone.shape_hash != card.shape_hash


def test_a_page_without_a_form_has_no_fields_and_is_unknown():
    challenge = _parse('<div id="content"><h1>Что-то новое</h1></div>')
    assert challenge.kind is SecurityChallengeKind.UNKNOWN
    assert challenge.fields == ()
    assert challenge.action is None
