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
        form = self.tree.css('div.page-content > form')[0]
        return OfferFields(
            raw_source=form.html or '',
            fields_dict=serialize_form(form),
        )
