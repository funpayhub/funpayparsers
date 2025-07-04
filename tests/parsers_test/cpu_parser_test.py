from funpayparsers.parsers.cpu_parser import (CurrentlyViewingOfferInfoParser,
                                              CurrentlyViewingOfferInfoParserOptions)


class TestCPUParsing:
    OPTIONS = CurrentlyViewingOfferInfoParserOptions(empty_raw_source=True)

    def test_cpu_parser(self, currently_viewing_offer_info_html,
                        currently_viewing_offer_info_obj):
        parser = CurrentlyViewingOfferInfoParser(currently_viewing_offer_info_html,
                                                 options=self.OPTIONS)
        assert parser.parse() == currently_viewing_offer_info_obj
