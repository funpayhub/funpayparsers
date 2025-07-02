__all__ = ('OfferFieldsParser', 'OfferFieldsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.utils import serialize_form
from funpayparsers.types.offers import OfferFields
from lxml import html


_EXCLUDE = ['csrf_token']


@dataclass(frozen=True)
class OfferFieldsParserOptions(FunPayObjectParserOptions):
    ...


class OfferFieldsParser(FunPayHTMLObjectParser[OfferFields, OfferFieldsParserOptions]):
    def _parse(self):
        form = self.tree.xpath('//form[1]')[0]
        fields = serialize_form(form)

        return OfferFields(
            raw_source=html.tostring(form, encoding='unicode'),
            csrf_token=fields['csrf_token'],
            other_fields={k: v for k, v in fields.items() if k not in _EXCLUDE},
        )
