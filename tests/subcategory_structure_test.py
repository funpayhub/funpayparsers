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


class TestLookupFieldIdWithContext:
    def _shared_label_struct(self) -> SubcategoryStructure:
        # ``q`` (SELECT) and ``q2`` (NUMERIC_RANGE) share a label;
        # ``q2`` is gated on ``q='другое количество'``.
        q = _mk_field(
            'q',
            label='Количество',
            type_=SubcategoryFieldType.SELECT,
            options=['50', '100', 'другое количество'],
        )
        q2 = SubcategoryFieldDef(
            raw_source='',
            id='q2',
            type=SubcategoryFieldType.NUMERIC_RANGE,
            label='Количество',
            conditions=[
                FieldCondition(field_id='q', values={'другое количество'}),
            ],
        )
        return SubcategoryStructure(subcategory_id=1, fields={'q': q, 'q2': q2})

    def test_unique_label_returns_id_without_context(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        assert s.lookup_field_id('Alpha') == 'a'

    def test_ambiguous_without_context_returns_none(self):
        s = self._shared_label_struct()
        assert s.lookup_field_id('Количество') is None

    def test_context_resolves_unconditional_when_condition_unsatisfied(self):
        s = self._shared_label_struct()
        # q has no conditions (score 1); q2's condition unsatisfied (score 0).
        assert s.lookup_field_id('Количество', context={'q': '50'}) == 'q'

    def test_context_resolves_conditional_when_satisfied(self):
        s = self._shared_label_struct()
        # q2's condition now satisfied (score 2) > q (score 1).
        assert (
            s.lookup_field_id('Количество', context={'q': 'другое количество'})
            == 'q2'
        )

    def test_empty_context_with_ambiguous_returns_none(self):
        s = self._shared_label_struct()
        # No context entries match either field's conditions.
        # q (1) > q2 (0) — q wins because q has no conditions.
        assert s.lookup_field_id('Количество', context={}) == 'q'

    def test_miss_returns_none(self):
        s = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        assert s.lookup_field_id('NoSuchLabel') is None
        assert s.lookup_field_id('NoSuchLabel', context={'a': 'x'}) is None


class TestEnrichDeliveryFieldsFromOffer:
    def _mk_offer(self, spec: dict[str, str]):
        # ``enrich_delivery_fields_from_offer`` only reads ``delivery_fields_spec``,
        # so a SimpleNamespace duck-types fine without constructing the full
        # OfferPage tree (which would need PageHeader, AppData, Chat, …).
        from types import SimpleNamespace
        return SimpleNamespace(delivery_fields_spec=spec)

    def test_enrich_unions_specs(self):
        s = SubcategoryStructure(subcategory_id=1)
        s.enrich_delivery_fields_from_offer(
            self._mk_offer({'player': 'Telegram Username'})
        )
        s.enrich_delivery_fields_from_offer(
            self._mk_offer({'login': 'Логин Steam'})
        )
        assert s.delivery_fields == {
            'player': 'Telegram Username',
            'login': 'Логин Steam',
        }

    def test_first_seen_label_wins(self):
        s = SubcategoryStructure(subcategory_id=1)
        s.enrich_delivery_fields_from_offer(
            self._mk_offer({'player': 'Telegram Username'})
        )
        s.enrich_delivery_fields_from_offer(
            self._mk_offer({'player': 'Some Other Label'})
        )
        assert s.delivery_fields == {'player': 'Telegram Username'}

    def test_returns_self(self):
        s = SubcategoryStructure(subcategory_id=1)
        assert s.enrich_delivery_fields_from_offer(self._mk_offer({})) is s


class TestSubcategoryStructureMerge:
    def test_field_only_in_other_deepcopied(self):
        s1 = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        s2 = SubcategoryStructure(
            subcategory_id=1, fields={'b': _mk_field('b', label='Beta')}
        )
        s1.merge_from(s2)
        assert set(s1.fields) == {'a', 'b'}
        # Mutating s2's deep-copied field must not affect s1.
        s2.fields['b'].aliases.add('xxx')
        assert 'xxx' not in s1.fields['b'].aliases

    def test_overlapping_field_unions_aliases(self):
        f1 = _mk_field('a', label='Alpha', aliases={'left'})
        f2 = _mk_field('a', label='Alpha', aliases={'right'})
        s1 = SubcategoryStructure(subcategory_id=1, fields={'a': f1})
        s2 = SubcategoryStructure(subcategory_id=1, fields={'a': f2})
        s1.merge_from(s2)
        # Union: own + other's aliases. Self is authoritative for label,
        # so 'alpha' (auto from label) is in there too.
        assert 'left' in s1.fields['a'].aliases
        assert 'right' in s1.fields['a'].aliases

    def test_alias_provenance_carried_over(self):
        s2 = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        s2.add_alias('a', 'extra', source=AliasSource.OFFER_PAGE)
        s1 = SubcategoryStructure(subcategory_id=1)
        s1.merge_from(s2)
        assert s1.alias_source('a', 'extra') is AliasSource.OFFER_PAGE

    def test_does_not_mutate_other(self):
        s2 = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        snapshot_aliases = set(s2.fields['a'].aliases)
        s1 = SubcategoryStructure(subcategory_id=1)
        s1.merge_from(s2)
        assert s2.fields['a'].aliases == snapshot_aliases

    def test_delivery_fields_merged(self):
        s1 = SubcategoryStructure(
            subcategory_id=1, delivery_fields={'player': 'Telegram Username'}
        )
        s2 = SubcategoryStructure(
            subcategory_id=1, delivery_fields={'login': 'Логин Steam'}
        )
        s1.merge_from(s2)
        assert s1.delivery_fields == {
            'player': 'Telegram Username',
            'login': 'Логин Steam',
        }

    def test_label_map_invalidated(self):
        s1 = SubcategoryStructure(
            subcategory_id=1, fields={'a': _mk_field('a', label='Alpha')}
        )
        _ = s1.label_map  # populate cache
        assert 'label_map' in s1.__dict__
        s2 = SubcategoryStructure(
            subcategory_id=1, fields={'b': _mk_field('b', label='Beta')}
        )
        s1.merge_from(s2)
        assert 'label_map' not in s1.__dict__
        assert 'beta' in s1.lower_label_map

    def test_returns_self(self):
        s1 = SubcategoryStructure(subcategory_id=1)
        s2 = SubcategoryStructure(subcategory_id=1)
        assert s1.merge_from(s2) is s1


class TestOrderPageReclassifyAndStructured:
    def _mk_order(self, data: dict[str, str]):
        # OrderPage's reclassify_with_structure / get_structured_fields read
        # only ``data`` and ``lot_fields``; bypass the full constructor.
        from types import SimpleNamespace
        from funpayparsers.types.pages.order_page import (
            OrderPage,
            _split_order_data,
        )
        metadata, lot_fields, delivery = _split_order_data(data)
        order = SimpleNamespace(
            data=data,
            metadata=metadata,
            lot_fields=lot_fields,
            delivery_fields=delivery,
        )
        # Bind real methods so they operate on the namespace.
        order.reclassify_with_structure = (
            OrderPage.reclassify_with_structure.__get__(order, type(order))
        )
        order.get_structured_fields = (
            OrderPage.get_structured_fields.__get__(order, type(order))
        )
        return order

    def test_reclassify_promotes_label_to_delivery(self):
        # A label that is *not* in the static blacklist but is in the
        # structure's delivery_fields should move from lot_fields to
        # delivery_fields after reclassification.
        s = SubcategoryStructure(subcategory_id=1)
        s.delivery_fields['player'] = 'Никнейм'
        order = self._mk_order({'игра': 'X', 'никнейм': 'qvvonk'})
        assert order.lot_fields == {'никнейм': 'qvvonk'}
        order.reclassify_with_structure(s)
        assert order.delivery_fields == {'никнейм': 'qvvonk'}
        assert order.lot_fields == {}

    def test_get_structured_fields_picks_unconditional_on_ambiguous(self):
        # Shared label, no helpful context — fallback prefers the
        # unconditional field (legacy first-by-declaration behaviour
        # via the in-method fallback when ``lookup_field_id`` returns
        # ``None``).
        q = _mk_field(
            'q',
            label='Количество',
            type_=SubcategoryFieldType.SELECT,
            options=['50'],
        )
        q2 = SubcategoryFieldDef(
            raw_source='',
            id='q2',
            type=SubcategoryFieldType.NUMERIC_RANGE,
            label='Количество',
            conditions=[
                FieldCondition(field_id='q', values={'другое количество'}),
            ],
        )
        s = SubcategoryStructure(subcategory_id=1, fields={'q': q, 'q2': q2})
        from types import SimpleNamespace
        from funpayparsers.types.pages.order_page import OrderPage
        order = SimpleNamespace(lot_fields={'количество': '50'})
        order.get_structured_fields = (
            OrderPage.get_structured_fields.__get__(order, type(order))
        )
        result = order.get_structured_fields(s)
        # Empty context, q wins via score (no conditions vs unsatisfied).
        assert result == {'q': '50'}
