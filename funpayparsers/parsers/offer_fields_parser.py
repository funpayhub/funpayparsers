__all__ = ('OfferFieldsParser', 'OfferFieldsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTML2ObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.utils import serialize_form
from funpayparsers.types.offers import OfferFields


_EXCLUDE = ['csrf_token']


@dataclass(frozen=True)
class OfferFieldsParserOptions(FunPayObjectParserOptions):
    ...


class OfferFieldsParser(FunPayHTML2ObjectParser[OfferFields, OfferFieldsParserOptions]):
    def _parse(self):
        form = self.tree.css('form')[0]
        fields = serialize_form(form)

        return OfferFields(
            raw_source=form.html,
            csrf_token=fields['csrf_token'],
            other_fields={k: v for k, v in fields.items() if k not in _EXCLUDE},
        )
