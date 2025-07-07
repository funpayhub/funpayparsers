__all__ = ('AppDataParsingOptions', 'AppDataParser')

from dataclasses import dataclass
import json
from funpayparsers.parsers.base import FunPayJSONObjectParser, ParsingOptions
from funpayparsers.types.common_page_elements import AppData, WebPush
from funpayparsers.types.enums import Language


@dataclass(frozen=True)
class AppDataParsingOptions(ParsingOptions):
    ...


class AppDataParser(FunPayJSONObjectParser[AppData, AppDataParsingOptions]):
    """
    Class for parsing AppData JSON.
    Possible locations:
        - Any FunPay page.
    """
    def _parse(self):
        webpush = self.data.get('webpush')
        if webpush is not None:
            webpush = WebPush(
                raw_source=json.dumps(webpush, ensure_ascii=False),
                app=webpush.get('app'),
                enabled=webpush.get('enabled'),
                hwid_required=webpush.get('hwid-required'),
            )

        return AppData(
            raw_source=self.raw_source,
            locale=Language.get_by_lang_code(self.data.get('locale')),
            csrf_token=self.data.get('csrf-token'),
            user_id=self.data.get('userId'),
            webpush=webpush
        )
