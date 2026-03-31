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

        field_schema: list[SubcategoryFieldDef] = []
        lot_fields_div = form.css_first('div.lot-fields', strict=False)
        if lot_fields_div is not None:
            raw_data_fields = lot_fields_div.attributes.get('data-fields', '[]') or '[]'
            fields_json: list[dict[str, Any]] = json.loads(
                html_module.unescape(raw_data_fields)
            )
            for fj in fields_json:
                field_schema.append(self._parse_field_def(fj, lot_fields_div))

        return OfferFields(
            raw_source=form.html or '',
            fields_dict=fields_dict,
            fields_names=field_names,
            field_schema=field_schema,
        )

    def _parse_field_def(
        self, field_json: dict[str, Any], lot_fields_div: LexborNode
    ) -> SubcategoryFieldDef:
        field_id: str = field_json['id']
        field_type = SubcategoryFieldType.from_type_int(field_json['type'])
        conditions = self._parse_conditions(field_json.get('conditions', []))

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

        options = self._parse_options(form_group, field_type)

        return SubcategoryFieldDef(
            raw_source=raw_source,
            id=field_id,
            type=field_type,
            label=label,
            conditions=conditions,
            options=options,
        )

    @staticmethod
    def _parse_conditions(raw_conditions: list[dict[str, Any]]) -> list[FieldCondition]:
        result = []
        for cond in raw_conditions:
            result.append(
                FieldCondition(
                    field_id=cond['id'],
                    values=cond.get(
                        'list', [cond['value']] if 'value' in cond else []
                    ),
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
        if select is None:
            return []
        return [
            str(opt.attributes['value'])
            for opt in select.css('option')
            if opt.attributes.get('value', '')
        ]
