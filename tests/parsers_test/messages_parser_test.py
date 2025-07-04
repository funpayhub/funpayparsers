from funpayparsers.parsers.messages_parser import MessagesParser, MessagesParserOptions


class TestMessagesParsing:
    OPTIONS = MessagesParserOptions(empty_raw_source=True)

    def test_messages_parsing(self, messages_data):
        html, obj = messages_data
        assert MessagesParser(html, self.OPTIONS).parse() == obj