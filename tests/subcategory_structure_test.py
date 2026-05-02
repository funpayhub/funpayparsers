from __future__ import annotations

import pytest

from funpayparsers.types import (
    FieldCondition,
    SubcategoryFieldDef,
    SubcategoryFieldType,
    SubcategoryStructure,
)


def _mk_field(
    field_id: str,
    label: str = '',
    type_: SubcategoryFieldType = SubcategoryFieldType.TEXT,
    aliases: set[str] | None = None,
    options: list[str] | None = None,
) -> SubcategoryFieldDef:
    return SubcategoryFieldDef(
        raw_source='',
        id=field_id,
        type=type_,
        label=label,
        conditions=[],
        options=options,
        aliases=aliases or set(),
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


class TestSubcategoryFieldDefAliases:
    def test_aliases_casefolded_in_post_init(self):
        f = _mk_field('weapon', label='Оружие', aliases={'Weapon', 'ОРУЖИЕ'})
        assert f.aliases == {'weapon', 'оружие'}

    def test_empty_aliases_filtered(self):
        f = _mk_field('a', aliases={'', 'X'})
        assert f.aliases == {'x'}


class TestSubcategoryStructureAliasIndexing:
    def test_label_map_includes_aliases(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'weapon': _mk_field(
                    'weapon', label='Оружие', aliases={'weapon', 'Категория'}
                ),
            },
        )
        # English ID and an extra localized alias both resolve to the field.
        assert s.lookup_field_id('Оружие') == 'weapon'
        assert s.lookup_field_id('weapon') == 'weapon'
        assert s.lookup_field_id('категория') == 'weapon'
        assert s.lookup_field_id('missing') is None

    def test_add_alias_invalidates_cache(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={'a': _mk_field('a', label='Alpha')},
        )
        # Touch caches.
        _ = s.label_map
        _ = s.lower_label_map
        s.add_alias('a', 'AltName')
        assert s.lookup_field_id('altname') == 'a'

    def test_enrich_from_offer_matches_unique_select_value(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'arena': _mk_field(
                    'arena',
                    label='Arena',
                    type_=SubcategoryFieldType.SELECT,
                    options=['15', '20', '30'],
                ),
            },
        )

        class _FakeOffer:
            fields = {'Арена': '15'}

        s.enrich_from_offer(_FakeOffer())  # type: ignore[arg-type]
        assert s.lookup_field_id('Арена') == 'arena'

    def test_enrich_from_offer_skips_ambiguous_match(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field(
                    'a',
                    label='A',
                    type_=SubcategoryFieldType.SELECT,
                    options=['x'],
                ),
                'b': _mk_field(
                    'b',
                    label='B',
                    type_=SubcategoryFieldType.SELECT,
                    options=['x'],
                ),
            },
        )

        class _FakeOffer:
            fields = {'Неизвестно': 'x'}

        s.enrich_from_offer(_FakeOffer())  # type: ignore[arg-type]
        assert s.lookup_field_id('Неизвестно') is None


class TestParseTitleFields:
    def _structure_with_select(self, options):
        return SubcategoryStructure(
            subcategory_id=1,
            fields={
                'quantity': _mk_field(
                    'quantity',
                    label='Quantity',
                    type_=SubcategoryFieldType.SELECT,
                    options=options,
                ),
            },
        )

    def test_select_quantity_collapsed_to_int(self):
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = self._structure_with_select(['50 звёзд', '100 звёзд'])
        result = _parse_title_fields('Telegram, 50 звёзд', s)
        assert result == {'quantity': 50}

    def test_select_non_numeric_option_kept_as_string(self):
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'currency': _mk_field(
                    'currency',
                    label='currency',
                    type_=SubcategoryFieldType.SELECT,
                    options=['USD', 'EUR', 'RUB'],
                ),
            },
        )
        result = _parse_title_fields('Card, USD', s)
        assert result == {'currency': 'USD'}

    def test_unknown_segment_dropped(self):
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = self._structure_with_select(['50 звёзд'])
        result = _parse_title_fields('Telegram, garbage', s)
        assert result == {}

    def test_numeric_range_extracted(self):
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'arena': _mk_field(
                    'arena', label='Arena', type_=SubcategoryFieldType.NUMERIC_RANGE
                ),
            },
        )
        assert _parse_title_fields('Lot, 15 арена', s) == {'arena': 15}

    def test_empty_title(self):
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        assert _parse_title_fields(None, self._structure_with_select(['x'])) == {}
        assert _parse_title_fields('', self._structure_with_select(['x'])) == {}

    def test_no_suffix_fields(self):
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={'a': _mk_field('a', label='A')},  # TEXT, not in suffix types
        )
        assert _parse_title_fields('anything, here', s) == {}
