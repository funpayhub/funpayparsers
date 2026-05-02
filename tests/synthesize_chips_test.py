from __future__ import annotations

import pytest

from funpayparsers.types.enums import SubcategoryType, SubcategoryFieldType
from funpayparsers.types.offers import OfferPreview
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.page_parsers.subcategory_page_parser import (
    _synthesize_chips_structure,
    SubcategoryPageParser,
    SubcategoryPageParsingOptions,
)


def _offer(
    other_data: dict[str, object] | None = None,
    other_data_names: dict[str, str] | None = None,
) -> OfferPreview:
    return OfferPreview(
        raw_source='',
        id=1,
        auto_delivery=False,
        is_pinned=False,
        title=None,
        amount=None,
        unit=None,
        price=MoneyValue(raw_source='', value=0, character='₽'),
        seller=None,
        other_data=other_data or {},
        other_data_names=other_data_names or {},
    )


class TestSynthesizeChipsStructure:
    def test_empty_offers_yields_empty_structure(self):
        s = _synthesize_chips_structure(subcategory_id=42, offers=[])
        assert s.subcategory_id == 42
        assert s.fields == {}
        assert s.derived_from == 'chips_offers'
        assert s.is_synthetic is True

    def test_single_offer_one_field(self):
        offers = [_offer(other_data={'server': 12448}, other_data_names={'server': 'Сервер'})]
        s = _synthesize_chips_structure(subcategory_id=173, offers=offers)
        assert set(s.fields) == {'server'}
        f = s.fields['server']
        assert f.type is SubcategoryFieldType.SELECT
        assert f.options == ['12448']
        assert f.label == 'Сервер'

    def test_options_accumulate_first_seen_order_across_offers(self):
        offers = [
            _offer(other_data={'server': 1, 'side': 'A'}),
            _offer(other_data={'server': 2, 'side': 'B'}),
            _offer(other_data={'server': 1, 'side': 'C'}),  # 1 already seen
        ]
        s = _synthesize_chips_structure(subcategory_id=1, offers=offers)
        assert s.fields['server'].options == ['1', '2']
        assert s.fields['side'].options == ['A', 'B', 'C']

    def test_label_falls_back_to_field_id(self):
        offers = [_offer(other_data={'server': 1})]
        s = _synthesize_chips_structure(subcategory_id=1, offers=offers)
        assert s.fields['server'].label == 'server'

    def test_authoritative_default_for_normal_constructor(self):
        # Sanity: structures built normally are not flagged synthetic.
        from funpayparsers.types.subcategory_structure import SubcategoryStructure
        s = SubcategoryStructure(subcategory_id=1, fields={})
        assert s.derived_from == 'lot_fields'
        assert s.is_synthetic is False


class TestFallbackOptionDefault:
    def test_option_defaults_to_off(self):
        # Opt-in: callers must explicitly enable to get synthetic structures.
        opts = SubcategoryPageParsingOptions()
        assert opts.fallback_structure_from_chips_offers is False
