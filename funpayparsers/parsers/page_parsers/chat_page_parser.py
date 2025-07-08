__all__ = ()

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.parsers.chat_previews_parser import PrivateChatPreviewsParser, PrivateChatPreviewParsingOptions
from funpayparsers.parsers.chat_parser import ChatParser, ChatParsingOptions
from funpayparsers.parsers.private_chat_info_parser import PrivateChatInfoParser, PrivateChatInfoParsingOptions
from funpayparsers.parsers.page_header_parser import PageHeaderParser, PageHeaderParsingOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.types.pages.chat_page import ChatPage


@dataclass(frozen=True)
class ChatPageParsingOptions(ParsingOptions):
    """Options class for ``ChatPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``ChatPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``ChatPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    private_chat_previews_parsing_options: PrivateChatPreviewParsingOptions = PrivateChatPreviewParsingOptions()
    """
    Options instance for ``PrivateChatPreviewsParser``, which is used by ``ChatPageParser``.

    Defaults to ``PrivateChatPreviewParsingOptions()``.
    """

    chat_parsing_options: ChatParsingOptions = ChatParsingOptions()
    """
    Options instance for ``ChatParser``, which is used by ``ChatPageParser``.

    Defaults to ``ChatParsingOptions()``.
    """

    private_chat_info_parsing_options: PrivateChatInfoParsingOptions = PrivateChatInfoParsingOptions()
    """
    Options instance for ``PrivateChatInfoParser``, which is used by ``ChatPageParser``.

    Defaults to ``PrivateChatInfoParsingOptions()``.
    """


class ChatPageParser(FunPayHTMLObjectParser[ChatPage, ChatPageParsingOptions]):
    """
    Class for parsing chat page (`https://funpay.com/chat/?node=<chat_id>`).
    """

    def _parse(self):
        header_div = self.tree.css_first('header')
        app_data = self.tree.css_first('body').attributes['data-app-data']

        chat_preview_div = self.tree.css('div.contact-list')
        chat_div = self.tree.css('div.chat:not(.chat-not-selected)')
        if not chat_div:
            chat = None
        else:
            chat = ChatParser(
                raw_source=chat_div[0].html,
                options=self.options.chat_parsing_options
            ).parse()

        if not chat_div:
            chat_info = None
        else:
            chat_info_div = self.tree.css('div.chat-detail-list:has(*)')
            if not chat_info_div:
                chat_info = None
            else:
                chat_info = PrivateChatInfoParser(
                    raw_source=chat_info_div[0].html,
                    options=self.options.chat_parsing_options
                ).parse()



        return ChatPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(header_div.html, options=self.options.page_header_parsing_options).parse(),
            app_data=AppDataParser(app_data, self.options.app_data_parsing_options).parse(),
            chat_previews=PrivateChatPreviewsParser(chat_preview_div[0].html, self.options.private_chat_previews_parsing_options).parse() if chat_preview_div else None,
            chat=chat,
            chat_info=chat_info
        )
