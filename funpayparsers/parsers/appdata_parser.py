from __future__ import annotations


__all__ = ('AppDataParsingOptions', 'AppDataParser')

import json
from dataclasses import dataclass

from funpayparsers.types.enums import Language
from funpayparsers.parsers.base import ParsingOptions, FunPayJSONObjectParser
from funpayparsers.types.common_page_elements import AppData, WebPush


@dataclass(frozen=True)
class AppDataParsingOptions(ParsingOptions):
    """Options class for ``AppDataParser``."""

    ...


class AppDataParser(FunPayJSONObjectParser[AppData, AppDataParsingOptions]):
    """
    Class for parsing AppData JSON.

    Possible locations:
        - Any FunPay page.
    """

    def _parse(self) -> AppData:
        webpush = self.data.get('webpush')  # type: ignore[union-attr] # raise Exception if not dict
        if webpush is not None:
            webpush = WebPush(
                raw_source=json.dumps(webpush, ensure_ascii=False),
                app=webpush.get('app'),
                enabled=webpush.get('enabled'),
                hwid_required=webpush.get('hwid-required'),
            )

        return AppData(
            raw_source=json.dumps(self.raw_source)
            if not isinstance(self.raw_source, str)
            else self.raw_source,
            locale=Language.get_by_lang_code(self.data.get('locale')),
            csrf_token=self.data.get('csrf-token'),
            user_id=self.data.get('userId'),
            webpush=webpush,
        )
