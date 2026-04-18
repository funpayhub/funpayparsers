from __future__ import annotations

import pytest

from funpayparsers.types import (
    FieldCondition,
    SubcategoryFieldDef,
    SubcategoryFieldType,
    SubcategoryStructure,
)


def _mk_field(field_id: str, label: str = '', type_: SubcategoryFieldType = SubcategoryFieldType.TEXT) -> SubcategoryFieldDef:
    return SubcategoryFieldDef(
        raw_source='',
        id=field_id,
        type=type_,
        label=label,
        conditions=[],
        options=None,
    )


class TestFieldCondition:
    def test_case_insensitive_match(self):
        c = FieldCondition(field_id='type', values={'С рейтингом'})
        assert c.is_satisfied_by('С рейтингом')
        assert c.is_satisfied_by('с рейтингом')
        assert c.is_satisfied_by('С РЕЙТИНГОМ')

    def test_no_match(self):
        c = FieldCondition(field_id='type', values={'yes'})
        assert not c.is_satisfied_by('no')
        assert not c.is_satisfied_by('')

    def test_numeric_value(self):
        c = FieldCondition(field_id='type', values={'1', '2'})
        assert c.is_satisfied_by(1)
        assert c.is_satisfied_by('2')
        assert not c.is_satisfied_by(3)

    def test_none_value(self):
        c = FieldCondition(field_id='type', values={'1'})
        assert not c.is_satisfied_by(None)

    def test_empty_values(self):
        c = FieldCondition(field_id='type', values=set())
        assert not c.is_satisfied_by('anything')


class TestSubcategoryStructureLabelMap:
    def test_unique_labels(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field('a', label='Alpha'),
                'b': _mk_field('b', label='Beta'),
            },
        )
        assert s.label_map == {'Alpha': ['a'], 'Beta': ['b']}
        assert s.lower_label_map == {'alpha': ['a'], 'beta': ['b']}

    def test_duplicate_labels_preserved_in_order(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field('a', label='X'),
                'b': _mk_field('b', label='X'),
                'c': _mk_field('c', label='Y'),
            },
        )
        assert s.label_map == {'X': ['a', 'b'], 'Y': ['c']}

    def test_empty_labels_grouped(self):
        # Regression: previously empty labels on unrelated fields would
        # silently overwrite each other in a dict[str, str] label_map.
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'type1': _mk_field('type1', label=''),
                'type2': _mk_field('type2', label=''),
            },
        )
        assert s.label_map == {'': ['type1', 'type2']}

    def test_case_insensitive_merge(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field('a', label='Rating'),
                'b': _mk_field('b', label='RATING'),
            },
        )
        assert s.lower_label_map == {'rating': ['a', 'b']}


class TestParsingErrorTruncation:
    def test_short_payload_kept(self):
        from funpayparsers.exceptions import ParsingError

        err = ParsingError('short' * 10)
        assert err.raw_source == 'short' * 10
        assert not err.raw_source_truncated

    def test_large_payload_truncated(self):
        from funpayparsers.exceptions import MAX_STORED_RAW_SOURCE, ParsingError

        payload = 'x' * (MAX_STORED_RAW_SOURCE * 4)
        err = ParsingError(payload)
        assert err.raw_source_truncated
        assert len(err.raw_source) < len(payload)
        assert '[truncated]' in err.raw_source

    def test_location_in_str(self):
        from funpayparsers.exceptions import ParsingError

        err = ParsingError('abc', location='arena field')
        assert 'arena field' in str(err)
