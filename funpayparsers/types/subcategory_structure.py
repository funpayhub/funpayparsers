from __future__ import annotations


__all__ = (
    'AliasSource',
    'FieldCondition',
    'SubcategoryFieldDef',
    'SubcategoryStructure',
)

import re
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal
from dataclasses import field, dataclass
from functools import cached_property
from collections.abc import Iterable

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import SubcategoryFieldType


if TYPE_CHECKING:
    from funpayparsers.types.offers import OfferFields, OfferPreview
    from funpayparsers.types.pages.offer_page import OfferPage
    from funpayparsers.types.pages.order_page import OrderPage


class AliasSource(str, Enum):
    """Provenance of a registered alias on a ``SubcategoryFieldDef``."""

    LABEL = 'label'
    """Auto-seeded from ``SubcategoryFieldDef.label`` at construction time."""

    LISTING = 'listing'
    """Listing page filter-form ``<label>`` text."""

    OFFER_EDIT = 'offer_edit'
    """OfferEdit form ``<label class="control-label">`` text."""

    OFFER_PAGE = 'offer_page'
    """Value-derived from ``OfferPage.fields``."""

    ORDER_PAGE = 'order_page'
    """Value-derived from ``OrderPage.lot_fields``."""

    OFFER_PREVIEW = 'offer_preview'
    """Derived from ``OfferPreview.other_data`` / ``other_data_names`` / title."""

    USER = 'user'
    """Explicitly registered by user code (default for ``add_alias``)."""


# Decorations sellers commonly inject into rendered values that are absent from
# the canonical filter-form options. The ranges deliberately cover only
# pictographic / symbol blocks — Latin, Cyrillic, digits, punctuation must pass
# through untouched.
_DECORATION_RE = re.compile(
    '['
    '\U0001F300-\U0001FAFF'   # extended pictographs (emoji proper)
    '\U00002600-\U000027BF'   # misc symbols + dingbats (★ ♠ ☂ ✋ …)
    '\U0001F1E6-\U0001F1FF'   # regional indicator symbols (flags)
    '⌀-⏿'           # misc technical (⌚ ⌛ ⏰ …)
    '⬀-⯿'           # misc symbols and arrows (⭐ ⬆ …)
    '✀-➿'           # dingbats (overlap with above, kept for clarity)
    '︀-️'           # variation selectors (incl. VS16 emoji style)
    '‍'                  # zero-width joiner (emoji combiner)
    ']+'
)


def _normalize_option(s: str) -> str:
    """
    Casefold + strip decorations + collapse whitespace + strip outer punctuation.

    Used for fuzzy comparison between canonical FunPay-form options (clean) and
    the user-rendered values that appear in offers/orders, where sellers
    commonly add emoji, stars, etc. (``'RUB🔥'`` vs option ``'RUB'``).
    """
    s = _DECORATION_RE.sub('', s)
    s = re.sub(r'\s+', ' ', s).strip(' .,!?·-—')
    return s.casefold()


@dataclass
class FieldCondition(FunPayObject):
    """
    Represents a visibility condition for a ``SubcategoryFieldDef``.

    The owning field is shown only when the field identified by ``field_id``
    has one of the values listed in ``values``.
    """

    raw_source: str = field(default='', compare=False)
    """Raw JSON of the condition object, if available."""

    field_id: str = ''
    """ID of the field whose value controls visibility of the owning field."""

    values: set[str] = field(default_factory=set)
    """
    Values of ``field_id`` that make the owning field visible.

    Sourced from the ``list`` key in the ``data-fields`` JSON condition object.
    Stored as a ``set`` — duplicates are not possible by definition.

    Values are compared case-insensitively in :meth:`is_satisfied_by`,
    because FunPay's public listing page and the ``offerEdit`` form render
    the same underlying value with inconsistent casing.
    """

    def __post_init__(self) -> None:
        self.values = {str(v).casefold() for v in self.values}

    def is_satisfied_by(self, value: Any) -> bool:
        """Return ``True`` if *value* (case-insensitively) is present in ``values``."""
        return str(value).casefold() in self.values


@dataclass
class SubcategoryFieldDef(FunPayObject):
    """Represents a single field definition within a subcategory."""

    id: str = ''
    """Field identifier as used by FunPay (e.g. ``'arena'``, ``'quantity'``)."""

    type: SubcategoryFieldType = SubcategoryFieldType.TEXT
    """Field type."""

    label: str = ''
    """Human-readable label from ``label.control-label`` in the form HTML."""

    conditions: list[FieldCondition] = field(default_factory=list)
    """
    Visibility conditions.

    Empty list means the field is always visible.
    The field is shown only when all conditions are satisfied simultaneously.
    """

    options: list[str] | None = None
    """
    Available option values for ``SELECT`` and ``DROPDOWN`` type fields.

    ``None`` for non-select fields (``NUMERIC_RANGE``, ``TEXT``, ``TEXTAREA``, ``IMAGES``).
    """

    aliases: set[str] = field(default_factory=set)
    """
    Additional, casefolded label aliases for this field.

    Used to bridge cross-locale label mismatches between the data-fields JSON
    (English IDs), the filter form ``<label>`` (locale-dependent), the
    per-offer ``param-list`` rendering, and ``OrderPage`` data labels.

    Always casefolded. The ``label`` itself is auto-added by ``__post_init__``,
    so callers never need to pass it explicitly. Additional aliases can be
    appended via :meth:`SubcategoryStructure.add_alias`.
    """

    def __post_init__(self) -> None:
        self.aliases = {str(a).casefold() for a in self.aliases if a}
        if self.label:
            self.aliases.add(self.label.casefold())


@dataclass
class SubcategoryStructure(FunPayObject):
    """
    Derived subcategory field structure for quick lookups.

    Built either from ``OfferFields`` (authenticated ``offerEdit`` page) or
    directly from the public subcategory listing page's ``div.lot-fields``.
    """

    raw_source: str = field(default='', compare=False)
    """Raw HTML of the ``div.lot-fields`` block, if available."""

    subcategory_id: int | None = None
    """Subcategory ID. ``None`` for currency (chips) offer fields."""

    fields: dict[str, SubcategoryFieldDef] = field(default_factory=dict)
    """
    Field definitions keyed by field ID, in declaration order.

    Use ``fields[field_id]`` for O(1) lookup by ID,
    or iterate over ``fields.values()`` to process fields in declaration order.
    """

    _alias_sources: dict[tuple[str, str], AliasSource] = field(default_factory=dict)
    """
    Provenance map: ``(field_id, alias_casefold) → source``.

    Tracks which enrich-source registered each alias. Defaults to
    :attr:`AliasSource.USER` for unspecified ``add_alias`` calls. Cleared
    selectively via :meth:`forget_aliases_from`.
    """

    delivery_fields: dict[str, str] = field(default_factory=dict)
    """
    Per-subcategory mapping of ``input.name → label`` for per-order
    delivery-contract fields, accumulated from observed offers via
    :meth:`enrich_delivery_fields_from_offer`.

    Distinct from :attr:`fields` (lot-config schema). These are buyer
    inputs (Telegram username, Steam login, …) that surface in
    :attr:`OrderPage.lot_fields` but should be classified as
    :attr:`OrderPage.delivery_fields` instead. Values are casefold-compared
    against ``OrderPage.data`` labels in
    :meth:`OrderPage.reclassify_with_structure`.
    """

    derived_from: Literal['lot_fields', 'chips_offers'] = 'lot_fields'
    """
    Provenance of this structure.

    * ``'lot_fields'`` — authoritative: parsed from a ``div.lot-fields``
      block (either listing page or authenticated ``offerEdit`` form).
    * ``'chips_offers'`` — synthetic: inferred from the union of
      ``OfferPreview.other_data`` keys/values across a sample of CHIPS
      offers, when the listing page has no ``div.lot-fields``. Field
      types default to ``SELECT``, options accumulate first-seen values.
    """

    def __post_init__(self) -> None:
        # Seed provenance for label-derived aliases that ``SubcategoryFieldDef``
        # auto-added in its own ``__post_init__``. Anything not yet tagged is
        # attributed to ``LABEL``; explicit enrich-from-* calls overwrite this.
        for fid, fd in self.fields.items():
            for alias in fd.aliases:
                self._alias_sources.setdefault((fid, alias), AliasSource.LABEL)

    @property
    def is_synthetic(self) -> bool:
        """``True`` iff ``derived_from`` is anything other than ``'lot_fields'``."""
        return self.derived_from != 'lot_fields'

    @cached_property
    def label_map(self) -> dict[str, list[str]]:
        """
        Mapping from FunPay label (or alias) to list of field IDs for reverse lookup.

        Indexes both ``f.label`` (as-is, possibly localized) and every entry in
        ``f.aliases`` (casefolded). Values are lists because different fields
        may share the same label/alias.
        """
        result: dict[str, list[str]] = {}
        for f in self.fields.values():
            seen: set[str] = set()
            for key in (f.label, *f.aliases):
                if key in seen:
                    continue
                seen.add(key)
                result.setdefault(key, []).append(f.id)
        return result

    @cached_property
    def lower_label_map(self) -> dict[str, list[str]]:
        """Case-insensitive variant of ``label_map`` — keys are casefolded."""
        result: dict[str, list[str]] = {}
        for label, ids in self.label_map.items():
            key = label.casefold()
            existing = result.setdefault(key, [])
            for fid in ids:
                if fid not in existing:
                    existing.append(fid)
        return result

    def lookup_field_id(
        self,
        label: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Resolve *label* (case-insensitively) to a single field ID.

        When *context* (mapping of already-resolved ``{field_id: value}`` pairs)
        is provided and *label* matches multiple fields, prefer the field whose
        visibility :attr:`SubcategoryFieldDef.conditions` are satisfied by
        *context*. Disambiguates fields that share a label in form-locale
        (``quantity`` SELECT vs ``quantity2`` NUMERIC_RANGE both labelled
        ``'Количество робуксов'``, where the latter is gated on
        ``quantity='другое количество'``).

        Returns ``None`` on miss, ``None`` on still-ambiguous match (no context,
        all-unsatisfied, or top-tier tie).
        """
        ids = self.lower_label_map.get(label.casefold())
        if not ids:
            return None
        if len(ids) == 1:
            return ids[0]
        if context is None:
            return None
        # Score per candidate:
        #   2 — has conditions, all satisfied by *context*;
        #   1 — has no conditions (always-visible);
        #   0 — has conditions but at least one unsatisfied.
        scored: list[tuple[int, str]] = []
        for fid in ids:
            conds = self.fields[fid].conditions
            if not conds:
                scored.append((1, fid))
                continue
            ok = all(
                c.field_id in context and c.is_satisfied_by(context[c.field_id])
                for c in conds
            )
            scored.append((2 if ok else 0, fid))
        scored.sort(key=lambda t: t[0], reverse=True)
        if scored[0][0] == 0:
            return None  # all unsatisfied
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            return None  # tie at top
        return scored[0][1]

    def add_alias(
        self,
        field_id: str,
        alias: str,
        source: AliasSource = AliasSource.USER,
    ) -> None:
        """
        Register *alias* for *field_id* and invalidate the cached label maps.

        *source* records the provenance of this alias for later inspection
        via :meth:`alias_source` or selective invalidation via
        :meth:`forget_aliases_from`. Re-registering an existing alias updates
        the recorded source.
        """
        if field_id not in self.fields or not alias:
            return
        casefolded = alias.casefold()
        if casefolded not in self.fields[field_id].aliases:
            self.fields[field_id].aliases.add(casefolded)
            self.__dict__.pop('label_map', None)
            self.__dict__.pop('lower_label_map', None)
        self._alias_sources[(field_id, casefolded)] = source

    def alias_source(self, field_id: str, alias: str) -> AliasSource | None:
        """Return the recorded source of *alias* for *field_id*, if any."""
        return self._alias_sources.get((field_id, alias.casefold()))

    def forget_aliases_from(self, source: AliasSource) -> int:
        """
        Drop every alias previously registered with *source*.

        Useful when re-enriching from a fresh sample — e.g.
        ``forget_aliases_from(AliasSource.OFFER_PAGE)`` before another
        ``enrich_from_offer`` pass to avoid stale value-derived aliases.

        Returns the number of aliases removed.
        """
        removed = 0
        for (fid, alias), src in list(self._alias_sources.items()):
            if src is source:
                fd = self.fields.get(fid)
                if fd is not None:
                    fd.aliases.discard(alias)
                del self._alias_sources[(fid, alias)]
                removed += 1
        if removed:
            self.__dict__.pop('label_map', None)
            self.__dict__.pop('lower_label_map', None)
        return removed

    def enrich_from_offer_fields(
        self, offer_fields: OfferFields
    ) -> SubcategoryStructure:
        """
        Add aliases from an authenticated ``OfferFields`` schema.

        Each ``SubcategoryFieldDef`` in *offer_fields.field_schema* carries a
        canonical localized ``label`` (text from ``<label class="control-label">``
        on the offerEdit form). Register that label as an alias for the matching
        field id in *self*.

        Use this once per subcategory to seed a structure built from the public
        listing page (which often renders English form labels) with the
        canonical localized labels FunPay uses elsewhere
        (``OrderPage.lot_fields`` keys, ``OfferPage.fields`` keys), bridging
        the listing-form / offer-page locale gap.

        Returns ``self`` for chaining. Mutates the underlying field defs.
        """
        for f in offer_fields.field_schema:
            if f.id in self.fields and f.label:
                self.add_alias(f.id, f.label, source=AliasSource.OFFER_EDIT)
        return self

    def enrich_from_offer(self, offer: OfferPage) -> SubcategoryStructure:
        """
        Add aliases from an ``OfferPage.fields`` mapping.

        For each ``(label, value)`` in ``offer.fields``:

        * If *label* already resolves via ``label_map`` — leave it alone.
        * Otherwise, try to match *value* against ``options`` of any
          ``SELECT``/``DROPDOWN`` field. If exactly one field matches,
          register *label* as an alias for that field.

        Returns ``self`` for chaining. Mutates the underlying field defs.
        """
        for label, value in offer.fields.items():
            if not label:
                continue
            if label.casefold() in self.lower_label_map:
                continue
            value_norm = _normalize_option(str(value))
            matches = [
                fid
                for fid, fd in self.fields.items()
                if fd.options
                and any(_normalize_option(opt) == value_norm for opt in fd.options)
            ]
            if len(matches) == 1:
                self.add_alias(matches[0], label, source=AliasSource.OFFER_PAGE)
        return self

    def enrich_from_order_page(self, order: OrderPage) -> SubcategoryStructure:
        """
        Add aliases from an ``OrderPage.lot_fields`` mapping.

        Mirror of :meth:`enrich_from_offer` but operates on completed-order
        data. For each ``(label, value)`` in ``order.lot_fields``:

        * If *label* already resolves via ``lower_label_map`` — leave it alone.
        * Otherwise, try to match *value* against ``options`` of any
          ``SELECT``/``DROPDOWN`` field. If exactly one field matches,
          register *label* as an alias for that field.

        Useful when callers have an ``OrderPage`` in hand (e.g. processing a
        ``NEW_ORDER`` message) and want to seed the structure without an extra
        ``OfferPage`` fetch.

        Returns ``self`` for chaining. Mutates the underlying field defs.
        """
        for label, value in order.lot_fields.items():
            if not label or label.casefold() in self.lower_label_map:
                continue
            value_norm = _normalize_option(str(value))
            matches = [
                fid
                for fid, fd in self.fields.items()
                if fd.options
                and any(_normalize_option(opt) == value_norm for opt in fd.options)
            ]
            if len(matches) == 1:
                self.add_alias(matches[0], label, source=AliasSource.ORDER_PAGE)
        return self

    def enrich_from_offer_previews(
        self, offers: Iterable[OfferPreview]
    ) -> SubcategoryStructure:
        """
        Add aliases from a batch of ``OfferPreview`` objects.

        For each offer, examines ``offer.other_data`` — the structured
        ``{field_id: value}`` pairs from the listing page's data-fields. When
        ``field_id`` already exists in *self.fields*, the corresponding
        ``other_data_names[field_id]`` (if any) is registered as an alias to
        ensure cross-locale lookups.

        Use this when processing a ``SubcategoryPage`` / ``MyOffersPage`` /
        ``ProfilePage`` where the offers are already in memory — no extra
        HTTP needed.

        Returns ``self`` for chaining. Mutates the underlying field defs.
        """
        for offer in offers:
            if not offer.other_data or not offer.other_data_names:
                continue
            for field_id in offer.other_data:
                if field_id not in self.fields:
                    continue
                name = offer.other_data_names.get(field_id)
                if name:
                    self.add_alias(
                        field_id, name, source=AliasSource.OFFER_PREVIEW
                    )
        return self

    def enrich_delivery_fields_from_offer(
        self, offer: OfferPage
    ) -> SubcategoryStructure:
        """
        Add delivery-contract field specs from :attr:`OfferPage.delivery_fields_spec`.

        Multiple offers in the same subcategory may share or extend each
        other's delivery contracts; this method unions them. Existing entries
        are preserved (first-seen label wins, via ``setdefault``) so the label
        seen on the first observed offer stays stable across the subcategory.

        Returns ``self`` for chaining. Mutates :attr:`delivery_fields`.
        """
        for name, label in offer.delivery_fields_spec.items():
            self.delivery_fields.setdefault(name, label)
        return self

    def merge_from(self, other: SubcategoryStructure) -> SubcategoryStructure:
        """
        Merge fields, aliases, and delivery specs from *other* into ``self``.

        * For each ``field_id`` only in *other* — deep-copy the whole
          ``SubcategoryFieldDef`` into ``self.fields`` and carry over its
          alias provenance.
        * For each ``field_id`` in **both** — union the alias sets only.
          ``self`` is treated as the authoritative source for ``label``,
          ``options``, ``type``, and ``conditions`` (other's values for
          these are ignored).
        * Provenance of newly-added aliases is taken from *other*'s
          ``_alias_sources``, falling back to :attr:`AliasSource.USER`.
        * :attr:`delivery_fields` (Task 1) — same first-seen-wins union.

        Use cases: combining a synthetic listing-derived structure with a
        ``from_offer_fields`` structure (complete but requires HTTP), or
        hydrating persistent-cached aliases on top of a freshly parsed one.

        Returns ``self`` for chaining. Does not mutate *other*.
        """
        from copy import deepcopy

        for fid, other_fd in other.fields.items():
            if fid not in self.fields:
                self.fields[fid] = deepcopy(other_fd)
                for alias in other_fd.aliases:
                    src = other._alias_sources.get((fid, alias), AliasSource.USER)
                    self._alias_sources[(fid, alias)] = src
                continue
            for alias in other_fd.aliases:
                if alias in self.fields[fid].aliases:
                    continue
                self.fields[fid].aliases.add(alias)
                src = other._alias_sources.get((fid, alias), AliasSource.USER)
                self._alias_sources[(fid, alias)] = src

        for name, label in other.delivery_fields.items():
            self.delivery_fields.setdefault(name, label)

        if self.fields:
            self.__dict__.pop('label_map', None)
            self.__dict__.pop('lower_label_map', None)
        return self

    @classmethod
    def from_offer_fields(cls, offer_fields: OfferFields) -> SubcategoryStructure:
        """
        Build a ``SubcategoryStructure`` from ``OfferFields``.

        :param offer_fields: An ``OfferFields`` instance returned by ``OfferFieldsParser``.
        :return: A ``SubcategoryStructure`` with field map and label maps populated.
        """
        return cls(
            raw_source=offer_fields.raw_source,
            subcategory_id=offer_fields.subcategory_id,
            fields={f.id: f for f in offer_fields.field_schema},
        )


