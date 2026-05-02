from __future__ import annotations

import pytest

from funpayparsers.types import (
    AliasSource,
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
        # Each label is auto-cased into the field's aliases by __post_init__,
        # so label_map indexes both the original label and the casefolded form.
        assert s.label_map == {
            'Alpha': ['a'],
            'alpha': ['a'],
            'Beta': ['b'],
            'beta': ['b'],
        }
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
        assert s.label_map == {
            'X': ['a', 'b'],
            'x': ['a', 'b'],
            'Y': ['c'],
            'y': ['c'],
        }

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

    def test_select_preferred_over_numeric_range_with_unsatisfied_conditions(self):
        """Regression: ``2000 RUB`` must hit ``rub`` (SELECT, option-exact),
        not ``inr2`` (NUMERIC_RANGE conditioned on ``inr='другое количество'``).

        Reproduces the gift-card subcat #1316 case observed live: structure has
        a dozen NUMERIC_RANGE fields (``usd2``/``rub2``/.../``inr2``), each
        gated by an unrelated parent value. Without condition-gating, every
        leading-numeric segment was greedily attributed to ``inr2`` (the last
        declared NUMERIC_RANGE), producing bogus extractions like
        ``{inr2: 2000, currency: 'RUB'}`` from ``'…, RUB, 2000 RUB'``.
        """
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        currency_fd = _mk_field(
            'currency',
            label='currency',
            type_=SubcategoryFieldType.SELECT,
            options=['USD', 'RUB', 'EUR'],
        )
        rub_fd = _mk_field(
            'rub',
            label='rub',
            type_=SubcategoryFieldType.SELECT,
            options=['500 RUB', '1000 RUB', '2000 RUB', '5000 RUB'],
        )
        rub_fd.conditions = [FieldCondition(field_id='currency', values={'rub'})]
        # NUMERIC_RANGE fields conditioned on values we do NOT see in the title
        inr2_fd = _mk_field(
            'inr2', label='Количество INR', type_=SubcategoryFieldType.NUMERIC_RANGE
        )
        inr2_fd.conditions = [FieldCondition(field_id='inr', values={'другое количество'})]
        rub2_fd = _mk_field(
            'rub2', label='Количество RUB', type_=SubcategoryFieldType.NUMERIC_RANGE
        )
        rub2_fd.conditions = [FieldCondition(field_id='rub', values={'другое количество'})]

        s = SubcategoryStructure(
            subcategory_id=1316,
            fields={'currency': currency_fd, 'rub': rub_fd, 'inr2': inr2_fd, 'rub2': rub2_fd},
        )

        result = _parse_title_fields(
            '🔑20 USD = 2000 РУБЛЕЙ💳ПОДАРОЧНАЯ КАРТА💳 iTunes(Россия), RUB, 2000 RUB',
            s,
        )
        assert result == {'currency': 'RUB', 'rub': 2000}

    def test_unconditional_numeric_range_still_matches(self):
        """NUMERIC_RANGE without conditions matches a leading-numeric segment.

        Counterpart to the regression test above — ensures we did not over-
        gate NUMERIC_RANGE matching.
        """
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'arena': _mk_field(
                    'arena', label='Arena', type_=SubcategoryFieldType.NUMERIC_RANGE
                ),
            },
        )
        # No conditions → still matches.
        assert _parse_title_fields('Some lot, 15 арена', s) == {'arena': 15}


class TestNormalizeOption:
    def test_strips_emoji(self):
        from funpayparsers.types.subcategory_structure import _normalize_option

        assert _normalize_option('RUB🔥') == 'rub'
        assert _normalize_option('🔥RUB') == 'rub'
        assert _normalize_option('По логину🔥') == 'по логину'

    def test_strips_misc_symbols_and_dingbats(self):
        from funpayparsers.types.subcategory_structure import _normalize_option

        assert _normalize_option('★★★Premium★★★') == 'premium'
        assert _normalize_option('⭐star') == 'star'
        assert _normalize_option('✋stop') == 'stop'

    def test_collapses_whitespace_and_strips_outer_punct(self):
        from funpayparsers.types.subcategory_structure import _normalize_option

        assert _normalize_option('  RUB  ') == 'rub'
        assert _normalize_option('rub.') == 'rub'
        assert _normalize_option('a   b') == 'a b'

    def test_preserves_letters_and_digits(self):
        from funpayparsers.types.subcategory_structure import _normalize_option

        # No false positives on the chars that actually carry meaning.
        assert _normalize_option('5000 RUB') == '5000 rub'
        assert _normalize_option('Логин Steam') == 'логин steam'
        assert _normalize_option('ChatGPT, Sora') == 'chatgpt, sora'


class TestEnrichFromOfferWithDecoratedValue:
    def test_emoji_decoration_resolves_to_clean_option(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'currency': _mk_field(
                    'currency',
                    label='currency',
                    type_=SubcategoryFieldType.SELECT,
                    options=['USD', 'RUB', 'EUR'],
                ),
            },
        )

        class _FakeOffer:
            fields = {'Тип валюты': 'RUB🔥'}

        s.enrich_from_offer(_FakeOffer())  # type: ignore[arg-type]
        assert s.lookup_field_id('Тип валюты') == 'currency'


class TestSubcategoryFieldDefLabelAutoAlias:
    def test_label_auto_added_to_aliases(self):
        f = _mk_field('login', label='Логин Steam')
        # __post_init__ adds the casefolded label to aliases automatically.
        assert 'логин steam' in f.aliases

    def test_empty_label_not_added(self):
        f = _mk_field('x', label='')
        assert f.aliases == set()


class TestEnrichFromOfferFields:
    def test_localized_label_registered_as_alias(self):
        from funpayparsers.types.offers import OfferFields

        # Listing-page structure renders English labels.
        s = SubcategoryStructure(
            subcategory_id=1086,
            fields={
                'login': _mk_field(
                    'login', label='login', type_=SubcategoryFieldType.TEXT
                ),
                'method': _mk_field(
                    'method',
                    label='method',
                    type_=SubcategoryFieldType.DROPDOWN,
                    options=['By login', 'As gift'],
                ),
            },
        )

        # offerEdit-page schema carries the canonical localized labels.
        offer_fields = OfferFields(
            raw_source='',
            field_schema=[
                _mk_field('login', label='Логин Steam', type_=SubcategoryFieldType.TEXT),
                _mk_field(
                    'method',
                    label='Способ пополнения',
                    type_=SubcategoryFieldType.DROPDOWN,
                    options=['По логину', 'Подарком'],
                ),
                # An id absent from the listing structure must be ignored.
                _mk_field('extra', label='Extra'),
            ],
        )

        s.enrich_from_offer_fields(offer_fields)

        assert s.lookup_field_id('Логин Steam') == 'login'
        assert s.lookup_field_id('Способ пополнения') == 'method'
        assert s.lookup_field_id('Extra') is None  # not in self.fields

    def test_chaining_returns_self(self):
        from funpayparsers.types.offers import OfferFields

        s = SubcategoryStructure(subcategory_id=1, fields={})
        of = OfferFields(raw_source='', field_schema=[])
        assert s.enrich_from_offer_fields(of) is s


class TestEnrichFromOrderPage:
    def _structure(self) -> SubcategoryStructure:
        return SubcategoryStructure(
            subcategory_id=1,
            fields={
                'currency': _mk_field(
                    'currency',
                    label='currency',
                    type_=SubcategoryFieldType.SELECT,
                    options=['RUB', 'USD'],
                ),
            },
        )

    def test_unique_value_match_registers_alias(self):
        s = self._structure()

        class _Order:
            lot_fields = {'тип валюты': 'RUB'}

        s.enrich_from_order_page(_Order())  # type: ignore[arg-type]
        assert s.lookup_field_id('тип валюты') == 'currency'
        assert s.alias_source('currency', 'тип валюты') is AliasSource.ORDER_PAGE

    def test_ambiguous_match_skipped(self):
        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field(
                    'a', label='A', type_=SubcategoryFieldType.SELECT, options=['x']
                ),
                'b': _mk_field(
                    'b', label='B', type_=SubcategoryFieldType.SELECT, options=['x']
                ),
            },
        )

        class _Order:
            lot_fields = {'неизвестно': 'x'}

        s.enrich_from_order_page(_Order())  # type: ignore[arg-type]
        assert s.lookup_field_id('неизвестно') is None

    def test_already_mapped_label_skipped(self):
        s = self._structure()
        # 'currency' already resolves; should not be touched.

        class _Order:
            lot_fields = {'currency': 'RUB'}

        s.enrich_from_order_page(_Order())  # type: ignore[arg-type]
        # No new ORDER_PAGE-source aliases were registered.
        assert all(
            src is not AliasSource.ORDER_PAGE
            for src in s._alias_sources.values()
        )


class TestEnrichFromOfferPreviews:
    def _structure(self) -> SubcategoryStructure:
        return SubcategoryStructure(
            subcategory_id=1,
            fields={
                'server': _mk_field('server', label='server'),
                'side': _mk_field('side', label='side'),
            },
        )

    def _preview(self, other_data, other_data_names, title=None):
        # Duck-typed stub — enrich_from_offer_previews only reads
        # ``other_data``, ``other_data_names`` and ``title``.
        class _P:
            pass

        p = _P()
        p.other_data = other_data
        p.other_data_names = other_data_names
        p.title = title
        return p

    def test_other_data_names_registered_as_aliases(self):
        s = self._structure()
        previews = [
            self._preview({'server': 12448}, {'server': 'Сервер'}),
            self._preview({'server': 12449}, {'server': 'Сервер'}),
            self._preview({'server': 12450, 'side': 1}, {'server': 'Сервер', 'side': 'Сторона'}),
        ]
        s.enrich_from_offer_previews(previews)
        assert s.lookup_field_id('Сервер') == 'server'
        assert s.lookup_field_id('Сторона') == 'side'
        assert s.alias_source('server', 'Сервер') is AliasSource.OFFER_PREVIEW

    def test_no_op_on_empty_inputs(self):
        s = self._structure()
        s.enrich_from_offer_previews([])
        s.enrich_from_offer_previews([self._preview({}, {})])
        # No previews and empty data should not crash and should not add
        # any OFFER_PREVIEW-sourced aliases.
        assert all(
            src is not AliasSource.OFFER_PREVIEW
            for src in s._alias_sources.values()
        )

    def test_unknown_field_id_ignored(self):
        s = self._structure()
        previews = [self._preview({'unknown': 1}, {'unknown': 'Что-то'})]
        s.enrich_from_offer_previews(previews)
        assert 'что-то' not in {a for fd in s.fields.values() for a in fd.aliases}


class TestAliasSource:
    def test_default_source_is_user(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='A')}
        )
        s.add_alias('a', 'Foo')
        assert s.alias_source('a', 'Foo') is AliasSource.USER

    def test_explicit_source_recorded(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='A')}
        )
        s.add_alias('a', 'Foo', source=AliasSource.OFFER_EDIT)
        assert s.alias_source('a', 'foo') is AliasSource.OFFER_EDIT

    def test_label_auto_aliases_seeded_with_label_source(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        assert s.alias_source('a', 'Alpha') is AliasSource.LABEL

    def test_forget_aliases_from_removes_only_matching_source(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        s.add_alias('a', 'FromOffer', source=AliasSource.OFFER_PAGE)
        s.add_alias('a', 'FromUser')  # USER
        # Trigger cache.
        _ = s.lower_label_map
        removed = s.forget_aliases_from(AliasSource.OFFER_PAGE)
        assert removed == 1
        assert s.lookup_field_id('FromOffer') is None
        assert s.lookup_field_id('FromUser') == 'a'
        # LABEL-seeded label is preserved.
        assert s.lookup_field_id('Alpha') == 'a'

    def test_add_alias_backward_compat_no_source_kwarg(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='A')}
        )
        # Calling without source still works (positional 2-arg form).
        s.add_alias('a', 'X')
        assert s.lookup_field_id('X') == 'a'


class TestParseTitleFieldsRightToLeft:
    def test_short_title_rightmost_match(self):
        """Title with as many segments as suffix fields, both validate."""
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'quantity': _mk_field(
                    'quantity',
                    label='quantity',
                    type_=SubcategoryFieldType.SELECT,
                    options=['50 звёзд', '100 звёзд'],
                ),
                'method': _mk_field(
                    'method',
                    label='method',
                    type_=SubcategoryFieldType.DROPDOWN,
                    options=['По username', 'Подарком'],
                ),
            },
        )
        assert _parse_title_fields('50 звёзд, По username', s) == {
            'quantity': 50,
            'method': 'По username',
        }

    def test_short_title_fewer_segments_than_fields(self):
        """Three suffix fields, only one matchable trailing segment — match
        from the right inward, leaving earlier fields unset."""
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field(
                    'a', label='a', type_=SubcategoryFieldType.SELECT,
                    options=['alpha'],
                ),
                'b': _mk_field(
                    'b', label='b', type_=SubcategoryFieldType.SELECT,
                    options=['beta'],
                ),
                'c': _mk_field(
                    'c', label='c', type_=SubcategoryFieldType.SELECT,
                    options=['gamma'],
                ),
            },
        )
        # Only 'gamma' is in any options — should match to 'c' only.
        assert _parse_title_fields('Free text, gamma', s) == {'c': 'gamma'}

    def test_unmatched_segment_skipped_for_earlier_field(self):
        """Free-form prefix segment doesn't get misassigned; an earlier field
        whose option matches a later segment still resolves."""
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'q': _mk_field(
                    'q', label='q', type_=SubcategoryFieldType.SELECT,
                    options=['50 звёзд'],
                ),
            },
        )
        assert _parse_title_fields('Random title text, 50 звёзд', s) == {'q': 50}

    def test_decorated_value_in_title_matches(self):
        """Seller-injected decoration in the title segment still resolves
        against the clean option list."""
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'currency': _mk_field(
                    'currency', label='currency',
                    type_=SubcategoryFieldType.SELECT,
                    options=['RUB', 'USD'],
                ),
            },
        )
        assert _parse_title_fields('Some lot, RUB🔥', s) == {'currency': 'RUB'}

    def test_unmatchable_segment_is_skipped_not_anchoring(self):
        """A rightmost segment that matches no field (e.g. order-amount
        ``'2 шт.'`` or seller-appended free text) is silently skipped, and
        the matcher continues scanning earlier segments. Without this
        behavior, valid suffix fields immediately to the left of garbage
        would be lost — which is what happened live on subcat #1316 with
        title ``'…, USD, 20 USD, 2 шт.'`` (the ``'2 шт.'`` is order
        metadata, not a structure field)."""
        from funpayparsers.types.subcategory_structure import _parse_title_fields

        s = SubcategoryStructure(
            subcategory_id=1,
            fields={
                'a': _mk_field(
                    'a', label='a', type_=SubcategoryFieldType.SELECT,
                    options=['x'],
                ),
            },
        )
        assert _parse_title_fields('x, garbage', s) == {'a': 'x'}
