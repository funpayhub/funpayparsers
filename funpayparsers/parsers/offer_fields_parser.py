__all__ = ('OfferFieldsParser', 'OfferFieldsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.utils import serialize_form
from funpayparsers.types.offers import OfferFields


@dataclass(frozen=True)
class OfferFieldsParserOptions(FunPayObjectParserOptions):
    ...


class OfferFieldsParser(FunPayHTMLObjectParser[OfferFields, OfferFieldsParserOptions]):
    """
    Class for parsing available offer fields.
    Possible locations:
        - On offer edit pages (https://funpay.com/lots/offerEdit?node=<node_id>&offer=<offer_id>)
    """
    def _parse(self):
        form = self.tree.css('form')[0]
        return OfferFields(
            raw_source=form.html,
            fields_dict=serialize_form(form),
        )
