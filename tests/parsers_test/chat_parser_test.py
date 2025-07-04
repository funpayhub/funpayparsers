from funpayparsers.parsers import ChatParserOptions, ChatParser


class TestChatParsing:
    OPTIONS = ChatParserOptions(empty_raw_source=True)

    def test_chat_parsing(self, chat_data):
        html, obj = chat_data
        assert ChatParser(html, options=self.OPTIONS).parse() == obj