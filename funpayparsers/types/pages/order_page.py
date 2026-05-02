from __future__ import annotations


__all__ = ('OrderPage', 'ORDER_METADATA_LABELS', 'ORDER_DELIVERY_LABELS')

import re
from typing import TYPE_CHECKING
from dataclasses import field, dataclass

from funpayparsers.types.chat import Chat
from funpayparsers.types.enums import OrderStatus, SubcategoryType
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.reviews import Review
from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.parsers.page_parsers.order_page_parser import OrderPageParsingOptions
    from funpayparsers.types.subcategory_structure import SubcategoryStructure


# Stable order-metadata labels rendered by FunPay regardless of the lot's
# subcategory. Keys are the canonical metadata names, values are the set of
# casefolded label variants that may appear in ``param-list`` (RU/EN/UA).
# Anything not in this map is treated as a lot-specific field and routed to
# ``OrderPage.lot_fields`` instead of ``OrderPage.metadata``.
ORDER_METADATA_LABELS: dict[str, frozenset[str]] = {
    'game': frozenset({'game', 'игра', 'гра'}),
    'category': frozenset({'category', 'категория', 'категорія'}),
    'short_description': frozenset(
        {'short description', 'краткое описание', 'короткий опис'}
    ),
    'detailed_description': frozenset(
        {'detailed description', 'подробное описание', 'докладний опис'}
    ),
    'amount': frozenset({'amount', 'количество', 'кількість'}),
    'open': frozenset({'open', 'открыт', 'відкрито'}),
    'closed': frozenset({'closed', 'закрыт', 'закрито'}),
    'total': frozenset({'total', 'сумма', 'сума'}),
}

_LABEL_TO_METADATA_KEY: dict[str, str] = {
    label: canonical
    for canonical, variants in ORDER_METADATA_LABELS.items()
    for label in variants
}


# Casefolded labels FunPay renders for buyer-supplied delivery-contract data
# in ``OrderPage.data`` (per-order, not lot-config). These should land in
# ``OrderPage.delivery_fields`` rather than ``lot_fields``. This static set
# covers common cases (Telegram username, Steam login, email, …) and acts as
# a fallback when no ``SubcategoryStructure.delivery_fields`` is available;
# see :meth:`OrderPage.reclassify_with_structure` for high-precision
# classification once a per-subcategory spec is on hand.
ORDER_DELIVERY_LABELS: frozenset[str] = frozenset({
    'telegram username',
    'логин steam',
    'steam login',
    'логин',
    'login',
    'почта',
    'email',
    'имя персонажа',
    'character name',
    'discord',
})


# Composite ``param-list`` labels of the form ``'<quantity-locale> <currency-id>'``
# that FunPay renders for currency-amount lot fields, e.g.
# ``'количество usd' = '20 USD'``, ``'количество rub' = '5000 RUB'``. The suffix
# is the canonical structure ``field_id`` (lowercase ASCII letters), so we can
# emit a synthetic ``lot_fields[currency_id] = '<numeric magnitude>'`` entry
# alongside the original label and unblock ``get_structured_fields`` lookups.
_COMPOSITE_LABEL_RE = re.compile(
    r'^(?:количество|quantity|кількість)\s+([a-z]{2,4})$'
)
_COMPOSITE_VALUE_RE = re.compile(r'^(\d+(?:\.\d+)?)\s+\S')


def _split_order_data(
    data: dict[str, str],
    expand_composite: bool = True,
    extra_delivery_labels: frozenset[str] = frozenset(),
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """
    Split ``param-list`` data into ``(metadata, lot_fields, delivery_fields)``.

    *data* keys are casefolded labels as parsed by ``OrderPageParser``.
    Routing rules, in order of precedence:

    1. Metadata labels (see :data:`ORDER_METADATA_LABELS`) → ``metadata`` under
       their canonical key.
    2. Delivery labels (:data:`ORDER_DELIVERY_LABELS` ∪ *extra_delivery_labels*,
       casefolded) → ``delivery_fields`` verbatim.
    3. Everything else → ``lot_fields`` verbatim.

    *extra_delivery_labels* lets callers pass a casefolded harvest of
    :attr:`SubcategoryStructure.delivery_fields` values for high-precision
    per-subcategory classification. Pass via
    :meth:`OrderPage.reclassify_with_structure` once a structure is on hand.

    When *expand_composite* is true (default), composite labels matching
    :data:`_COMPOSITE_LABEL_RE` (e.g. ``'количество usd'``) are *additionally*
    indexed in ``lot_fields`` under the trailing currency id with the bare
    numeric magnitude as value, so ``get_structured_fields`` can resolve them
    against the structure's ``usd``/``rub``/``eur``/… fields. The original
    composite label is always kept verbatim for back-compat. If the synthetic
    key already exists in ``lot_fields`` (rare collision), the original entry
    wins (``setdefault`` semantics).

    All three resulting dicts are pairwise disjoint by key.
    """
    metadata: dict[str, str] = {}
    lot_fields: dict[str, str] = {}
    delivery_fields: dict[str, str] = {}
    delivery_set = ORDER_DELIVERY_LABELS | extra_delivery_labels
    for label, value in data.items():
        canonical = _LABEL_TO_METADATA_KEY.get(label)
        if canonical is not None and canonical not in metadata:
            metadata[canonical] = value
            continue
        if label in delivery_set:
            delivery_fields[label] = value
            continue
        lot_fields[label] = value
        if expand_composite:
            cm = _COMPOSITE_LABEL_RE.match(label)
            if cm is not None:
                vm = _COMPOSITE_VALUE_RE.match(value)
                if vm is not None:
                    lot_fields.setdefault(cm.group(1), vm.group(1))
    return metadata, lot_fields, delivery_fields


@dataclass
class OrderPage(FunPayPage):
    """Represents an order page (`https://funpay.com/orders/<order_id>/`)."""

    order_id: str
    """Order ID."""

    order_status: OrderStatus
    """Order status."""

    delivered_goods: list[str] | None
    """List of delivered goods."""

    images: list[str] | None
    """List of attached images."""

    order_subcategory_id: int
    """Order subcategory id."""

    order_subcategory_type: SubcategoryType
    """Order subcategory type."""

    data: dict[str, str]
    """
    Raw, flat ``param-list`` data — keys are casefolded labels.

    Kept for backwards compatibility. Prefer ``metadata`` for stable
    order-level fields and ``lot_fields`` for lot-specific fields.
    """

    review: Review | None
    """Order review."""

    chat: Chat
    """Chat with counterparty."""

    metadata: dict[str, str] = field(default_factory=dict)
    """
    Stable order metadata, keyed by canonical name (see
    :data:`ORDER_METADATA_LABELS`). Possible keys: ``game``, ``category``,
    ``short_description``, ``detailed_description``, ``amount``, ``open``,
    ``closed``, ``total``. Only keys actually present on the page are stored.
    """

    lot_fields: dict[str, str] = field(default_factory=dict)
    """
    Lot-specific fields from ``param-list`` — everything in ``data`` that is
    neither :attr:`metadata` nor :attr:`delivery_fields`. Keys are casefolded
    labels, values are display strings. This is the input for
    :meth:`get_structured_fields`.
    """

    delivery_fields: dict[str, str] = field(default_factory=dict)
    """
    Per-order delivery-contract data supplied by the buyer at checkout
    (Telegram username, Steam login, character name, email, …). Classified
    via the static :data:`ORDER_DELIVERY_LABELS` blacklist at parse time;
    callers can re-classify with higher precision via
    :meth:`reclassify_with_structure` once a ``SubcategoryStructure`` with
    populated :attr:`SubcategoryStructure.delivery_fields` is available.
    """

    def get_structured_fields(self, structure: SubcategoryStructure) -> dict[str, str]:
        """
        Return ``lot_fields`` remapped to FunPay field IDs.

        Resolves each label via :meth:`SubcategoryStructure.lookup_field_id`,
        passing the already-resolved entries as *context* so condition-gated
        fields (e.g. ``quantity2`` NUMERIC_RANGE shadowing ``quantity`` SELECT)
        disambiguate against shared labels. Falls back to first-by-declaration
        when context is insufficient, preserving legacy behaviour.
        """
        result: dict[str, str] = {}
        for label, val in self.lot_fields.items():
            fid = structure.lookup_field_id(label, context=result)
            if fid is None:
                ids = structure.lower_label_map.get(label.casefold())
                if ids:
                    fid = ids[0]
            if fid is not None:
                result[fid] = val
        return result

    def reclassify_with_structure(
        self, structure: SubcategoryStructure
    ) -> OrderPage:
        """
        Re-split :attr:`data` using ``structure.delivery_fields`` for
        high-precision delivery classification.

        Useful when the page was originally parsed without structure context
        (only :data:`ORDER_DELIVERY_LABELS` static blacklist applied), and the
        caller has since obtained a ``SubcategoryStructure`` enriched via
        :meth:`SubcategoryStructure.enrich_delivery_fields_from_offer`.

        Mutates :attr:`metadata`, :attr:`lot_fields`, :attr:`delivery_fields`
        in place and returns ``self`` for chaining.
        """
        extra = frozenset(
            label.casefold() for label in structure.delivery_fields.values()
        )
        metadata, lot_fields, delivery_fields = _split_order_data(
            self.data, extra_delivery_labels=extra
        )
        self.metadata = metadata
        self.lot_fields = lot_fields
        self.delivery_fields = delivery_fields
        return self

    @property
    def short_description(self) -> str | None:
        """Order short description (title)."""
        return self.metadata.get('short_description')

    @property
    def full_description(self) -> str | None:
        """Order full description (detailed description)."""
        return self.metadata.get('detailed_description')

    @property
    def amount(self) -> int | None:
        amount_str = self.metadata.get('amount')
        if not amount_str:
            return None
        return int(re.search(r'\d+', amount_str).group())  # type: ignore[union-attr]
        # always has \d+

    @property
    def open_date_text(self) -> str | None:
        """Order open date."""
        date_str = self.metadata.get('open')
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def close_date_text(self) -> str | None:
        """Order close date."""
        date_str = self.metadata.get('closed')
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def order_category_name(self) -> str | None:
        """Order category name."""
        return self.metadata.get('game')

    @property
    def order_subcategory_name(self) -> str | None:
        """Order subcategory name."""
        return self.metadata.get('category')

    @property
    def order_total(self) -> MoneyValue | None:
        """Order total."""
        from funpayparsers.parsers.utils import parse_money_value_string

        value = self.metadata.get('total')
        if not value:
            return None
        return parse_money_value_string(value)

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: OrderPageParsingOptions | None = None
    ) -> OrderPage:
        from funpayparsers.parsers.page_parsers.order_page_parser import (
            OrderPageParser,
            OrderPageParsingOptions,
        )

        options = options or OrderPageParsingOptions()
        return OrderPageParser(raw_source=raw_source, options=options).parse()
