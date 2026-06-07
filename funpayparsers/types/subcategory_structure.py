from __future__ import annotations


__all__ = ('FieldCondition', 'SubcategoryFieldDef', 'SubcategoryStructure')

import re
from typing import TYPE_CHECKING
from dataclasses import field, dataclass

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.enums import SubcategoryFieldType


if TYPE_CHECKING:
    from funpayparsers.types.offers import OfferFields


_TITLE_SUFFIX_TYPES = frozenset({
    SubcategoryFieldType.NUMERIC_RANGE,
    SubcategoryFieldType.SELECT,
    SubcategoryFieldType.DROPDOWN,
})


def _parse_title_fields(title: str, structure: SubcategoryStructure) -> dict[str, str | int]:
    """
    Extract field values from a comma-separated offer title suffix.

    FunPay appends ``NUMERIC_RANGE``, ``SELECT``, and ``DROPDOWN`` field values
    to the offer title in declaration order, separated by ``', '``.

    Returns a mapping of field ID → parsed value.  ``NUMERIC_RANGE`` values are
    returned as ``int`` (the leading numeric portion is extracted).
    """
    suffix_fields = [f for f in structure.fields if f.type in _TITLE_SUFFIX_TYPES]
    if not suffix_fields:
        return {}
    parts = title.rsplit(', ', maxsplit=len(suffix_fields))
    result: dict[str, str | int] = {}
    for field_def, raw_val in zip(suffix_fields, parts[1:]):
        if field_def.type is SubcategoryFieldType.NUMERIC_RANGE:
            m = re.match(r'^(\d+(?:\.\d+)?)', raw_val.strip())
            result[field_def.id] = int(float(m.group(1))) if m else raw_val
        else:
            result[field_def.id] = raw_val
    return result


@dataclass
class FieldCondition:
    """
    Represents a visibility condition for a ``SubcategoryFieldDef``.

    The owning field is shown only when the field identified by ``field_id``
    has one of the values listed in ``values``.
    """

    field_id: str
    """ID of the field whose value controls visibility of the owning field."""

    values: list[str]
    """
    Values of ``field_id`` that make the owning field visible.

    Sourced from the ``list`` key in the ``data-fields`` JSON condition object.
    """


@dataclass
class SubcategoryFieldDef(FunPayObject):
    """Represents a single field definition within a subcategory."""

    id: str
    """Field identifier as used by FunPay (e.g. ``'arena'``, ``'quantity'``)."""

    type: SubcategoryFieldType
    """Field type."""

    label: str
    """Human-readable label from ``label.control-label`` in the form HTML."""

    conditions: list[FieldCondition]
    """
    Visibility conditions.

    Empty list means the field is always visible.
    The field is shown only when all conditions are satisfied simultaneously.
    """

    options: list[str] | None
    """
    Available option values for ``SELECT`` and ``DROPDOWN`` type fields.

    ``None`` for non-select fields (``NUMERIC_RANGE``, ``TEXT``, ``TEXTAREA``, ``IMAGES``).
    """


@dataclass
class SubcategoryStructure:
    """
    Derived subcategory field structure for quick lookups.

    Not a ``FunPayObject`` — constructed from ``OfferFields.field_schema``
    rather than parsed directly from HTML.

    Use ``SubcategoryStructure.from_offer_fields()`` to build an instance
    from a parsed ``OfferFields``.
    """

    subcategory_id: int | None
    """Subcategory ID. ``None`` for currency (chips) offer fields."""

    fields: list[SubcategoryFieldDef]
    """All field definitions in declaration order."""

    field_map: dict[str, SubcategoryFieldDef] = field(compare=False)
    """Mapping from field ID to its definition for O(1) lookup."""

    label_map: dict[str, str] = field(compare=False)
    """Mapping from FunPay label to field ID for reverse lookup."""

    lower_label_map: dict[str, str] = field(compare=False)
    """Case-insensitive variant of ``label_map`` — keys are lowercased."""

    @classmethod
    def from_offer_fields(cls, offer_fields: OfferFields) -> SubcategoryStructure:
        """
        Build a ``SubcategoryStructure`` from a parsed ``OfferFields`` instance.

        :param offer_fields: An ``OfferFields`` instance returned by ``OfferFieldsParser``.
        :return: A ``SubcategoryStructure`` with field map and label map populated.
        """
        fields = offer_fields.field_schema
        label_map = {f.label: f.id for f in fields}
        return cls(
            subcategory_id=offer_fields.subcategory_id,
            fields=fields,
            field_map={f.id: f for f in fields},
            label_map=label_map,
            lower_label_map={k.lower(): v for k, v in label_map.items()},
        )
