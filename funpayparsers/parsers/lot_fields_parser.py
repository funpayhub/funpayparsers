__all__ = ('LotFieldsParser', 'LotFieldsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.utils import serialize_form
from funpayparsers.types.lots import LotFields
from lxml import html


_EXCLUDE = ['csrf_token']


@dataclass(frozen=True)
class LotFieldsParserOptions(FunPayObjectParserOptions):
    ...


class LotFieldsParser(FunPayObjectParser[LotFields, LotFieldsParserOptions]):

    __options_cls__ = LotFieldsParserOptions

    def _parse(self):
        form = self.tree.xpath('//form[1]')[0]
        fields = serialize_form(form)

        return LotFields(
            raw_source=html.tostring(form, encoding='unicode'),
            csrf_token=form['csrf_token'],
            other_fields={k: v for k, v in fields.items() if k in _EXCLUDE},
        )
