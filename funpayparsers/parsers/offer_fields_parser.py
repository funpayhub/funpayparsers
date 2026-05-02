from __future__ import annotations


__all__ = ('OfferFieldsParser', 'OfferFieldsParsingOptions')

import html as html_module
import json
from typing import Any
from dataclasses import dataclass

from selectolax.lexbor import LexborNode

from funpayparsers.types.enums import SubcategoryFieldType
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferFields
from funpayparsers.parsers.utils import serialize_form
from funpayparsers.types.subcategory_structure import FieldCondition, SubcategoryFieldDef


@dataclass(frozen=True)
class OfferFieldsParsingOptions(ParsingOptions):
    """Options class for ``OfferFieldsParser``."""

    ...


class OfferFieldsParser(FunPayHTMLObjectParser[OfferFields, OfferFieldsParsingOptions]):
    """
    Class for parsing available offer fields.

    Possible locations:
        - Offer creating page (`https://funpay.com/lots/offerEdit?node=<node_id>`)
        - Offer editing page
        (`https://funpay.com/lots/offerEdit?node=<node_id>&offer=<offer_id>`)

    .. note::
        Both pages are auth-only. The public subcategory listing page
        (`https://funpay.com/lots/<id>/`) carries a compatible slimmed-down
        ``data-fields`` JSON together with per-field form groups, and can be
        parsed into a (partial) :class:`SubcategoryStructure` — see
        :class:`SubcategoryPageParser`, which does this automatically.
    """

    def _parse(self) -> OfferFields:
        form = self.tree.css('div.page-content > form')[0]
        fields_dict = serialize_form(form)

        field_names = {}
        for k in fields_dict:
            node = form.css_first(f'[name="{k}"]', strict=False, default=None)
            if node is None or node.attributes.get('type') == 'hidden':
                continue

            parent = node.parent
            if parent is None:
                continue
            label = parent.css_first('label.control-label', strict=False, default=None)
            if label is None:
                continue
            field_names[k] = label.text(strip=True)

        lot_fields_div = form.css_first('div.lot-fields', strict=False)
        field_schema = self.parse_field_schema(lot_fields_div) if lot_fields_div else []

        return OfferFields(
            raw_source=form.html or '',
            fields_dict=fields_dict,
            fields_names=field_names,
            field_schema=field_schema,
        )

    @classmethod
    def parse_field_schema(
        cls, lot_fields_div: LexborNode
    ) -> list[SubcategoryFieldDef]:
        """
        Parse the ``data-fields`` JSON on a ``div.lot-fields`` node into a
        list of :class:`SubcategoryFieldDef`.

        This is shared by the authenticated ``offerEdit`` flow and the
        anonymous subcategory listing flow, because both render the same
        ``data-fields`` attribute and the same per-field markup.
        """
        raw_data_fields = lot_fields_div.attributes.get('data-fields', '[]') or '[]'
        fields_json: list[dict[str, Any]] = json.loads(html_module.unescape(raw_data_fields))
        return [cls._parse_field_def(fj, lot_fields_div) for fj in fields_json]

    @classmethod
    def _parse_field_def(
        cls, field_json: dict[str, Any], lot_fields_div: LexborNode
    ) -> SubcategoryFieldDef:
        field_id: str = field_json['id']
        field_type = SubcategoryFieldType.from_type_code(field_json['type'])
        conditions = cls._parse_conditions(field_json.get('conditions', []))

        # Prefer non-locale div, then Russian locale, then any locale.
        form_group = (
            lot_fields_div.css_first(
                f'div.form-group.lot-field[data-id="{field_id}"]:not([data-locale])',
                strict=False,
            )
            or lot_fields_div.css_first(
                f'div.form-group.lot-field[data-id="{field_id}"][data-locale="ru"]',
                strict=False,
            )
            or lot_fields_div.css_first(
                f'div.form-group.lot-field[data-id="{field_id}"]',
                strict=False,
            )
        )

        if form_group is not None:
            label_node = form_group.css_first('label.control-label', strict=False)
            label = label_node.text(strip=True) if label_node else field_id
            raw_source = form_group.html or ''
        else:
            label = field_id
            raw_source = ''

        options = cls._parse_options(form_group, field_type)

        # Index the field's own ID as an alias so cross-locale lookups
        # (data-fields JSON key vs. localized ``<label>``) resolve to the same
        # field via ``label_map``. The label itself is auto-added by
        # ``SubcategoryFieldDef.__post_init__``.
        return SubcategoryFieldDef(
            raw_source=raw_source,
            id=field_id,
            type=field_type,
            label=label,
            conditions=conditions,
            options=options,
            aliases={field_id},
        )

    @staticmethod
    def _parse_conditions(raw_conditions: list[dict[str, Any]]) -> list[FieldCondition]:
        result: list[FieldCondition] = []
        for cond in raw_conditions:
            if 'list' in cond:
                values = cond['list']
            elif 'value' in cond:
                values = [cond['value']]
            else:
                raise ValueError(
                    f'Unrecognized condition format: {cond!r}. '
                    f"Expected one of 'list' or 'value' keys."
                )
            result.append(
                FieldCondition(
                    raw_source=json.dumps(cond, ensure_ascii=False),
                    field_id=cond['id'],
                    values=set(values),
                )
            )
        return result

    @staticmethod
    def _parse_options(
        form_group: LexborNode | None, field_type: SubcategoryFieldType
    ) -> list[str] | None:
        if field_type not in (SubcategoryFieldType.SELECT, SubcategoryFieldType.DROPDOWN):
            return None
        if form_group is None:
            return []
        select = form_group.css_first('select.lot-field-input', strict=False)
        if select is not None:
            return [
                str(opt.attributes['value'])
                for opt in select.css('option')
                if opt.attributes.get('value', '')
            ]
        # Public listing pages render the same options as a button group
        # (<div class="lot-field-radio-box"><button value="...">).
        # Empty value is the "All" button and must be skipped.
        return [
            str(btn.attributes['value'])
            for btn in form_group.css('.lot-field-radio-box button[value]')
            if btn.attributes.get('value', '')
        ]
