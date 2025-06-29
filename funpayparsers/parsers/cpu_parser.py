__all__ = ('CurrentlyViewingOfferInfoParserOptions', 'CurrentlyViewingOfferInfoParser')


from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.types.common import CurrentlyViewingOfferInfo
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentlyViewingOfferInfoParserOptions(FunPayObjectParserOptions):
    ...


class CurrentlyViewingOfferInfoParser(FunPayHTMLObjectParser[
                                          CurrentlyViewingOfferInfo,
                                          CurrentlyViewingOfferInfoParserOptions
                                      ]):
    def _parse(self):
        link = self.tree.xpath('//a[1]')[0]
        url = link.get('href')
        id_ = url.split('id=')[-1]
        text = link.text.strip()

        return CurrentlyViewingOfferInfo(
            raw_source=self.raw_source,
            id=int(id_) if id_.isnumeric() else id_,
            name=text
        )
