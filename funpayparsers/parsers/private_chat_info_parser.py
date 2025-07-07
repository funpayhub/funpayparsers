__all__ = ('PrivateChatInfoParsingOptions', 'PrivateChatInfoParser')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.parsers.cpu_parser import CurrentlyViewingOfferInfoParser, CurrentlyViewingOfferInfoParsingOptions
from funpayparsers.types.chat import PrivateChatInfo


@dataclass(frozen=True)
class PrivateChatInfoParsingOptions(ParsingOptions):
    cpu_parsing_options: CurrentlyViewingOfferInfoParsingOptions = CurrentlyViewingOfferInfoParsingOptions()


class PrivateChatInfoParser(FunPayHTMLObjectParser[PrivateChatInfo, PrivateChatInfoParsingOptions]):
    """
    Class for parsing private chat info block.
    Possible locations:
        - On opened private chat page (https://funpay.com/chat/?node=<chat_id>)
    """

    def _parse(self):
        info_div = self.tree.css('div.chat-detail-list')[0]
        blocks = info_div.css('div.param-item')

        result = PrivateChatInfo(
            raw_source=info_div.html,
            registration_date_text=blocks[0].text(separator='\n', strip=True).strip().split('\n')[-2],
            language=None,
            currently_viewing_offer=None
        )
        blocks.pop(0)

        for div in blocks:
            if div.attributes.get('data-type') == 'c-p-u':
                cpu = CurrentlyViewingOfferInfoParser(raw_source=div.html,
                                                      options=self.options.cpu_parsing_options & self.options).parse()
                result.currently_viewing_offer = cpu
            else:
                result.language = div.css('div')[0].text(separator='\n', strip=True).strip().split('\n')[-1].strip()

        return result
