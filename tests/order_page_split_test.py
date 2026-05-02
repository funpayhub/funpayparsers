from __future__ import annotations

from funpayparsers.types.pages.order_page import (
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
        metadata, lot_fields = _split_order_data(data)

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
        metadata, lot_fields = _split_order_data(data)
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
        metadata, lot_fields = _split_order_data(data)
        assert metadata == {
            'game': 'CSGO',
            'short_description': 'Skin',
            'detailed_description': 'Long text',
            'open': '01.01.2026',
            'closed': '02.01.2026',
        }
        assert lot_fields == {}
