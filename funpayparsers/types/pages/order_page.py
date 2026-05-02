from __future__ import annotations


__all__ = ('OrderPage', 'ORDER_METADATA_LABELS')

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
) -> tuple[dict[str, str], dict[str, str]]:
    """
    Split ``param-list`` data into ``(metadata, lot_fields)``.

    *data* keys are casefolded labels as parsed by ``OrderPageParser``.
    Metadata labels (see :data:`ORDER_METADATA_LABELS`) are extracted under
    their canonical key; everything else is preserved verbatim in
    ``lot_fields``.

    When *expand_composite* is true (default), composite labels matching
    :data:`_COMPOSITE_LABEL_RE` (e.g. ``'количество usd'``) are *additionally*
    indexed in ``lot_fields`` under the trailing currency id with the bare
    numeric magnitude as value, so ``get_structured_fields`` can resolve them
    against the structure's ``usd``/``rub``/``eur``/… fields. The original
    composite label is always kept verbatim for back-compat. If the synthetic
    key already exists in ``lot_fields`` (rare collision), the original entry
    wins (``setdefault`` semantics).
    """
    metadata: dict[str, str] = {}
    lot_fields: dict[str, str] = {}
    for label, value in data.items():
        canonical = _LABEL_TO_METADATA_KEY.get(label)
        if canonical is not None and canonical not in metadata:
            metadata[canonical] = value
            continue
        lot_fields[label] = value
        if expand_composite:
            cm = _COMPOSITE_LABEL_RE.match(label)
            if cm is not None:
                vm = _COMPOSITE_VALUE_RE.match(value)
                if vm is not None:
                    lot_fields.setdefault(cm.group(1), vm.group(1))
    return metadata, lot_fields


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
    not part of ``metadata``. Keys are casefolded labels, values are display
    strings. This is the input for :meth:`get_structured_fields`.
    """

    def get_structured_fields(self, structure: SubcategoryStructure) -> dict[str, str]:
        """Return ``lot_fields`` remapped to FunPay field IDs using *structure*'s label map."""
        return {
            structure.lower_label_map[label][0]: val
            for label, val in self.lot_fields.items()
            if label in structure.lower_label_map
        }

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
