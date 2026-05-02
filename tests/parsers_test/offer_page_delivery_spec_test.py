from __future__ import annotations

from selectolax.lexbor import LexborHTMLParser

from funpayparsers.parsers.page_parsers.offer_page_parser import (
    _parse_delivery_fields_spec,
)


def _form(html: str):
    return LexborHTMLParser(f'<form action="/orders/new">{html}</form>').css_first(
        'form'
    )


class TestParseDeliveryFieldsSpec:
    def test_basic_telegram_username(self):
        node = _form(
            '<div class="form-group">'
            '<label class="control-label">Telegram Username</label>'
            '<input name="player" type="text">'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {'player': 'Telegram Username'}

    def test_skips_payment_method_dropdown(self):
        node = _form(
            '<div class="form-group">'
            '<label class="control-label">Способ оплаты</label>'
            '<select name="method"><option>x</option></select>'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {}

    def test_skips_chrome_autofill_hidden_input(self):
        node = _form(
            '<div class="form-group">'
            '<label class="control-label">dummy</label>'
            '<input name="username" type="hidden">'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {}

    def test_skips_calc_box_form_groups(self):
        node = _form(
            '<div class="form-group offer-calc-box">'
            '<label class="control-label">Сумма</label>'
            '<input name="sum" type="text">'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {}

    def test_skips_unlabeled_groups(self):
        node = _form(
            '<div class="form-group">'
            '<input name="weird" type="text">'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {}

    def test_multiple_visible_fields(self):
        node = _form(
            '<div class="form-group">'
            '<label class="control-label">Логин Steam</label>'
            '<input name="login" type="text"></div>'
            '<div class="form-group">'
            '<label class="control-label">Email</label>'
            '<input name="email" type="email"></div>'
        )
        assert _parse_delivery_fields_spec(node) == {
            'login': 'Логин Steam',
            'email': 'Email',
        }

    def test_skips_reserved_csrf_token(self):
        node = _form(
            '<div class="form-group">'
            '<label class="control-label">irrelevant</label>'
            '<input name="csrf_token" type="text">'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {}

    def test_first_named_input_wins(self):
        # form-group with hidden offer_id followed by text input — the text
        # input is the delivery field; reserved name is filtered out, then
        # the next input is picked up.
        node = _form(
            '<div class="form-group">'
            '<label class="control-label">Имя персонажа</label>'
            '<input name="character_name" type="text">'
            '</div>'
        )
        assert _parse_delivery_fields_spec(node) == {
            'character_name': 'Имя персонажа',
        }
