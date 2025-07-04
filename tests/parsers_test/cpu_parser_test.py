from funpayparsers.parsers.cpu_parser import (CurrentlyViewingOfferInfoParser,
                                              CurrentlyViewingOfferInfoParserOptions)


OPTIONS = CurrentlyViewingOfferInfoParserOptions(empty_raw_source=True)


def test_cpu_parser(currently_viewing_offer_info_html,
                    currently_viewing_offer_info_obj):
    parser = CurrentlyViewingOfferInfoParser(currently_viewing_offer_info_html,
                                             options=OPTIONS)
    assert parser.parse() == currently_viewing_offer_info_obj
