from __future__ import annotations


__all__ = ('PrivateChatInfoParsingOptions', 'PrivateChatInfoParser')

from dataclasses import dataclass

from funpayparsers.types.chat import PrivateChatInfo
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.cpu_parser import (
    CurrentlyViewingOfferInfoParser,
    CurrentlyViewingOfferInfoParsingOptions,
)


@dataclass(frozen=True)
class PrivateChatInfoParsingOptions(ParsingOptions):
    """Options class for ``PrivateChatInfoParser``."""

    cpu_parsing_options: CurrentlyViewingOfferInfoParsingOptions = (
        CurrentlyViewingOfferInfoParsingOptions()
    )
    """
    Options instance for ``CurrentlyViewingOfferInfoParser``,
    which is used by ``PrivateChatInfoParser``.

    Defaults to ``CurrentlyViewingOfferInfoParsingOptions()``.
    """


class PrivateChatInfoParser(
    FunPayHTMLObjectParser[PrivateChatInfo, PrivateChatInfoParsingOptions],
):
    """
    Class for parsing private chat info block.

    Possible locations:
        - Private chat pages (`https://funpay.com/chat/?node=<chat_id>`)
    """

    def _parse(self) -> PrivateChatInfo:
        info_div = self.tree.css('div.chat-detail-list')[0]
        blocks = info_div.css('div.param-item:not(.hidden)')

        result = PrivateChatInfo(
            raw_source=info_div.html or '',
            registration_date_text=(
                blocks[0].text(separator='\n', strip=True).strip().split('\n')[-2]
            ),
            language=None,
            currently_viewing_offer=None,
        )
        blocks.pop(0)

        for div in blocks:
            if div.attributes.get('data-type') == 'c-p-u':
                cpu = CurrentlyViewingOfferInfoParser(
                    raw_source=div.html or '',
                    options=self.options.cpu_parsing_options,
                ).parse()
                result.currently_viewing_offer = cpu
            else:
                result.language = (
                    div.css('div')[0]
                    .text(separator='\n', strip=True)
                    .strip()
                    .split('\n')[-1]
                    .strip()
                )

        return result
