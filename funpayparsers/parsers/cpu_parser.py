__all__ = ('CurrentlyViewingOfferInfoParserOptions', 'CurrentlyViewingOfferInfoParser')


from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.types.updates import CurrentlyViewingOfferInfo
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentlyViewingOfferInfoParserOptions(FunPayObjectParserOptions):
    ...


class CurrentlyViewingOfferInfoParser(FunPayHTMLObjectParser[
                                          CurrentlyViewingOfferInfo,
                                          CurrentlyViewingOfferInfoParserOptions
                                      ]):
    """
    Class for parsing C-P-U data (which offer specific user is currently viewing).
    Possible locations:
        - On private chat pages (https://funpay.com/chat/?node=<chat_id>).
        - In runners response.
    """
    def _parse(self):
        link = self.tree.css('a')[0]
        url = link.attributes['href']
        id_ = url.split('id=')[-1]

        return CurrentlyViewingOfferInfo(
            raw_source=self.raw_source,
            id=int(id_) if id_.isnumeric() else id_,
            name=link.text(strip=True)
        )
