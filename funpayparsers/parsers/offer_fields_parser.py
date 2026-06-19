from __future__ import annotations


__all__ = ('OfferFieldsParser', 'OfferFieldsParsingOptions')

from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferFields
from funpayparsers.parsers.utils import serialize_form


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
        # The authenticated ``offerEdit`` page wraps the form in
        # ``div.page-content``. Other callers (e.g. ``MyChipsPageParser``) pass
        # the bare ``<form>`` HTML, where that wrapper is absent — fall back to
        # a plain ``form`` lookup in that case. When there is no form at all
        # (empty/unrelated source), return empty fields instead of failing.
        form_nodes = self.tree.css('div.page-content > form') or self.tree.css('form')
        if not form_nodes:
            return OfferFields(raw_source='')
        form = form_nodes[0]
        fields_dict = serialize_form(form)

        field_names = {}
        for k in fields_dict:
            node = form.css_first(f'[name="{k}"]', strict=False, default=None)
            if node is None or node.attributes.get('type') == 'hidden':
                continue

            label = node.parent.css_first('label.control-label', strict=False, default=None)
            if label is None:
                continue
            field_names[k] = label.text(strip=True)

        return OfferFields(
            raw_source=form.html or '', fields_dict=fields_dict, fields_names=field_names
        )
