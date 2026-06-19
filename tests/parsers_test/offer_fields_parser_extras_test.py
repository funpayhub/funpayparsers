from __future__ import annotations

from funpayparsers.parsers.offer_fields_parser import OfferFieldsParser


class TestParseRobustness:
    def test_empty_source_yields_empty_fields(self):
        result = OfferFieldsParser('').parse()

        assert result.fields_dict == {}
        assert result.fields_names == {}

    def test_source_without_form_yields_empty_fields(self):
        result = OfferFieldsParser('<div>no form here</div>').parse()

        assert result.fields_dict == {}

    def test_bare_form_without_page_content_wrapper(self):
        # Regression: `MyChipsPageParser` feeds the bare `<form>` HTML, which is
        # not wrapped in `div.page-content`. The parser must fall back to a plain
        # `form` lookup instead of raising on an empty selector result.
        result = OfferFieldsParser(
            '<form class="form-ajax-simple" method="post">'
            '<input type="hidden" name="game" value="41">'
            '<input type="text" name="chip" value="gold">'
            '</form>'
        ).parse()

        assert result.fields_dict == {'game': '41', 'chip': 'gold'}
