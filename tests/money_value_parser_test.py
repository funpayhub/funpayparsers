from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.enums import Currency


OPTIONS = MoneyValueParserOptions(empty_raw_source=True)


explicitly_positive_value_html = """"""

explicitly_positive_value_obj = ...

positive_value_html = """"""

positive_value_obj = ...

negative_value_html = """"""

negative_value_obj = ...


def test_explicitly_positive_value_parsing():
    parser = MoneyValueParser(explicitly_positive_value_html, options=OPTIONS)
    assert parser.parse() == explicitly_positive_value_obj


def test_positive_value_parsing():
    parser = MoneyValueParser(positive_value_html, options=OPTIONS)
    assert parser.parse() == positive_value_obj


def test_negative_value_parsing():
    parser = MoneyValueParser(negative_value_html, options=OPTIONS)
    assert parser.parse() == negative_value_obj
