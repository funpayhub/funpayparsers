from __future__ import annotations


__all__ = ('CurrentlyViewingOfferInfoParsingOptions', 'CurrentlyViewingOfferInfoParser')


from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import CurrentlyViewingOfferInfo


@dataclass(frozen=True)
class CurrentlyViewingOfferInfoParsingOptions(ParsingOptions):
    """Options class for ``CurrentlyViewingOfferInfoParser``."""

    ...


class CurrentlyViewingOfferInfoParser(
    FunPayHTMLObjectParser[
        CurrentlyViewingOfferInfo,
        CurrentlyViewingOfferInfoParsingOptions,
    ]
):
    """
    Class for parsing C-P-U data (which offer specific user is currently viewing).
    Possible locations:
        - Private chat pages (`https://funpay.com/chat/?node=<chat_id>`).
        - Runner response.
    """

    def _parse(self) -> CurrentlyViewingOfferInfo:
        link = self.tree.css('a')[0]
        url: str = link.attributes['href']  # type: ignore[assignment] # always has href
        id_ = url.split('id=')[-1]

        return CurrentlyViewingOfferInfo(
            raw_source=self.raw_source,
            id=int(id_) if id_.isnumeric() else id_,
            title=link.text(strip=True),
        )
