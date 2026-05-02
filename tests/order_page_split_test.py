from __future__ import annotations

from funpayparsers.types.pages.order_page import (
    ORDER_DELIVERY_LABELS,
    ORDER_METADATA_LABELS,
    _split_order_data,
)


class TestSplitOrderData:
    def test_metadata_extracted_under_canonical_keys(self):
        data = {
            'игра': 'ChatGPT',
            'категория': 'Telegram Stars',
            'количество': '50 шт.',
            'сумма': '100 ₽',
            'тип валюты': 'USD',
            'количество usd': '10',
        }
        metadata, lot_fields, _delivery = _split_order_data(data)

        assert metadata == {
            'game': 'ChatGPT',
            'category': 'Telegram Stars',
            'amount': '50 шт.',
            'total': '100 ₽',
        }
        assert lot_fields == {
            'тип валюты': 'USD',
            'количество usd': '10',
        }

    def test_metadata_keys_disjoint_from_lot_field_keys(self):
        # No raw label appears under both buckets (the dicts use different
        # key spaces: canonical names vs. raw labels).
        data = {'игра': 'g', 'custom': 'x'}
        metadata, lot_fields, _delivery = _split_order_data(data)
        assert set(metadata.keys()).isdisjoint(lot_fields.keys())
        assert 'custom' in lot_fields
        assert metadata == {'game': 'g'}

    def test_english_locale(self):
        data = {
            'game': 'CSGO',
            'short description': 'Skin',
            'detailed description': 'Long text',
            'open': '01.01.2026',
            'closed': '02.01.2026',
        }
        metadata, lot_fields, _delivery = _split_order_data(data)
        assert metadata == {
            'game': 'CSGO',
            'short_description': 'Skin',
            'detailed_description': 'Long text',
            'open': '01.01.2026',
            'closed': '02.01.2026',
        }
        assert lot_fields == {}


class TestSplitOrderDataCompositeExpansion:
    def test_composite_label_expanded(self):
        data = {'количество usd': '20 USD', 'игра': 'App Store'}
        metadata, lot_fields, _delivery = _split_order_data(data)
        assert metadata == {'game': 'App Store'}
        assert lot_fields == {'количество usd': '20 USD', 'usd': '20'}

    def test_composite_rub_expanded(self):
        data = {'количество rub': '5000 RUB'}
        _, lot_fields, _ = _split_order_data(data)
        assert lot_fields == {'количество rub': '5000 RUB', 'rub': '5000'}

    def test_unknown_unit_token_still_split(self):
        # The regex accepts any 2-4 letter currency-id-style suffix so we stay
        # robust to FunPay adding new currencies. The split happens whenever the
        # value also matches '<number> <token>'.
        data = {'количество gbp': '100 GBP'}
        _, lot_fields, _ = _split_order_data(data)
        assert lot_fields == {'количество gbp': '100 GBP', 'gbp': '100'}

    def test_non_numeric_value_not_split(self):
        data = {'количество usd': 'free'}
        _, lot_fields, _ = _split_order_data(data)
        # No numeric magnitude → no synthetic entry, original preserved.
        assert lot_fields == {'количество usd': 'free'}

    def test_existing_synthetic_key_not_overwritten(self):
        data = {'usd': 'preexisting', 'количество usd': '20 USD'}
        _, lot_fields, _ = _split_order_data(data)
        # setdefault: original wins on collision.
        assert lot_fields['usd'] == 'preexisting'
        assert lot_fields['количество usd'] == '20 USD'

    def test_expand_composite_off_disables_split(self):
        data = {'количество usd': '20 USD'}
        _, lot_fields, _ = _split_order_data(data, expand_composite=False)
        assert lot_fields == {'количество usd': '20 USD'}

    def test_label_not_composite_unchanged(self):
        data = {'тип валюты': 'USD'}
        _, lot_fields, _ = _split_order_data(data)
        assert lot_fields == {'тип валюты': 'USD'}


class TestSplitOrderDataDeliveryClassification:
    def test_static_blacklist_routes_to_delivery(self):
        data = {
            'игра': 'Telegram Stars',
            'telegram username': '@nimda',
            'количество': '50 шт.',
        }
        metadata, lot_fields, delivery = _split_order_data(data)
        assert metadata == {'game': 'Telegram Stars', 'amount': '50 шт.'}
        assert delivery == {'telegram username': '@nimda'}
        assert lot_fields == {}

    def test_steam_login_routed_to_delivery(self):
        data = {'логин steam': 'qvvonk', 'регион': 'EU'}
        _, lot_fields, delivery = _split_order_data(data)
        assert delivery == {'логин steam': 'qvvonk'}
        assert lot_fields == {'регион': 'EU'}

    def test_extra_delivery_labels_extends_blacklist(self):
        data = {'некий новый delivery': 'value', 'регион': 'EU'}
        _, lot_fields, delivery = _split_order_data(
            data,
            extra_delivery_labels=frozenset({'некий новый delivery'}),
        )
        assert delivery == {'некий новый delivery': 'value'}
        assert lot_fields == {'регион': 'EU'}

    def test_extra_delivery_labels_does_not_replace_static(self):
        data = {'telegram username': '@nimda'}
        _, _, delivery = _split_order_data(
            data, extra_delivery_labels=frozenset({'irrelevant'})
        )
        assert delivery == {'telegram username': '@nimda'}

    def test_three_dicts_pairwise_disjoint(self):
        data = {
            'игра': 'Steam',
            'telegram username': '@x',
            'регион': 'EU',
            'количество usd': '20 USD',
        }
        metadata, lot_fields, delivery = _split_order_data(data)
        keys_m, keys_l, keys_d = (
            set(metadata),
            set(lot_fields),
            set(delivery),
        )
        assert keys_m & keys_l == set()
        assert keys_m & keys_d == set()
        assert keys_l & keys_d == set()

    def test_delivery_label_in_constants(self):
        assert 'telegram username' in ORDER_DELIVERY_LABELS
        assert 'логин steam' in ORDER_DELIVERY_LABELS
