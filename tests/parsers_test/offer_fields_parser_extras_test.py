from __future__ import annotations

import pytest
from selectolax.lexbor import LexborHTMLParser

from funpayparsers.parsers.offer_fields_parser import OfferFieldsParser
from funpayparsers.types.enums import SubcategoryFieldType


class TestParseConditions:
    def test_list_form(self):
        result = OfferFieldsParser._parse_conditions(
            [{'id': 'type', 'list': ['a', 'b']}]
        )
        assert len(result) == 1
        assert result[0].field_id == 'type'
        # values are casefold-normalized in FieldCondition.__post_init__
        assert result[0].values == {'a', 'b'}

    def test_value_form(self):
        result = OfferFieldsParser._parse_conditions(
            [{'id': 'type', 'value': 'c'}]
        )
        assert result[0].values == {'c'}

    def test_unknown_form_raises(self):
        with pytest.raises(ValueError, match='Unrecognized condition format'):
            OfferFieldsParser._parse_conditions([{'id': 'type', 'huh': 'x'}])


class TestParseOptions:
    @staticmethod
    def _mk_form_group(html: str):
        tree = LexborHTMLParser(html)
        return tree.css_first('div.form-group')

    def test_non_select_returns_none(self):
        fg = self._mk_form_group('<div class="form-group"></div>')
        assert OfferFieldsParser._parse_options(fg, SubcategoryFieldType.TEXT) is None
        assert OfferFieldsParser._parse_options(fg, SubcategoryFieldType.IMAGES) is None

    def test_select_source(self):
        fg = self._mk_form_group(
            '<div class="form-group">'
            '  <select class="lot-field-input">'
            '    <option value="">All</option>'
            '    <option value="pve">PvE</option>'
            '    <option value="pvp">PvP</option>'
            '  </select>'
            '</div>'
        )
        assert OfferFieldsParser._parse_options(fg, SubcategoryFieldType.SELECT) == ['pve', 'pvp']

    def test_radio_box_source_on_listing_page(self):
        # Regression: the subcategory listing page renders SELECT fields
        # as button groups rather than <select>. The parser must recognize
        # both and skip the empty "All" button.
        fg = self._mk_form_group(
            '<div class="form-group">'
            '  <div class="lot-field-radio-box">'
            '    <button type="button" value="">All</button>'
            '    <button type="button" value="pve">PvE</button>'
            '    <button type="button" value="pvp">PvP</button>'
            '  </div>'
            '</div>'
        )
        assert OfferFieldsParser._parse_options(fg, SubcategoryFieldType.SELECT) == ['pve', 'pvp']

    def test_missing_form_group(self):
        assert OfferFieldsParser._parse_options(None, SubcategoryFieldType.SELECT) == []
