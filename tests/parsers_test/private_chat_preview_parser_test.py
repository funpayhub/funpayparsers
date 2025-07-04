from funpayparsers.parsers import PrivateChatPreviewParserOptions, PrivateChatPreviewParser


class TestPrivateChatPreviewsParsing:
    OPTIONS = PrivateChatPreviewParserOptions(empty_raw_source=True)

    def test_private_chat_preview_parsing(self, private_chat_preview_data):
        html, obj = private_chat_preview_data
        assert PrivateChatPreviewParser(html, self.OPTIONS).parse() == obj