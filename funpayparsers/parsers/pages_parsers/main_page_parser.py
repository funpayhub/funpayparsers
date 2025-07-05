__all__ = ('MainPageParser', 'MainPageParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.categories_parser import CategoriesParser, CategoriesParserOptions
from funpayparsers.parsers.chat_parser import ChatParser, ChatParserOptions
from funpayparsers.parsers.page_header_parser import PageHeaderParser, PageHeaderParserOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParserOptions
from funpayparsers.types.pages.main_page import MainPage


@dataclass(frozen=True)
class MainPageParserOptions(FunPayObjectParserOptions):
    header_parser_options: PageHeaderParserOptions = PageHeaderParserOptions()
    app_data_parser_options: AppDataParserOptions = AppDataParserOptions()
    categories_parser_options: CategoriesParserOptions = CategoriesParserOptions()
    chat_parser_options: ChatParserOptions = ChatParserOptions()


class MainPageParser(FunPayHTMLObjectParser[MainPage, MainPageParserOptions]):
    """
    Class for parsing FunPay main page.
    Possible locations:
        - https://funpay.com/
    """

    def _parse(self):
        header_div = self.tree.css('header')[0]
        categories_divs = self.tree.css('div.promo-game-list')
        if len(categories_divs) == 1:
            last_categories = []
            categories = CategoriesParser(categories_divs[0].html,
                                          options=self.options.categories_parser_options).parse()
        else:
            last_categories = CategoriesParser(categories_divs[0].html,
                                          options=self.options.categories_parser_options).parse()
            categories = CategoriesParser(categories_divs[1].html,
                                          options=self.options.categories_parser_options).parse()

        secret_chat_div = self.tree.css('div.chat')[0]

        appdata = self.tree.css('body')[0].attrs.get('data-app-data')

        return MainPage(
            raw_source=self.tree.html,
            header=PageHeaderParser(header_div.html, options=self.options.header_parser_options).parse(),
            last_categories=last_categories,
            categories=categories,
            secret_chat=ChatParser(secret_chat_div.html, options=self.options.chat_parser_options).parse(),
            app_data=AppDataParser(appdata, self.options.app_data_parser_options).parse()
        )
