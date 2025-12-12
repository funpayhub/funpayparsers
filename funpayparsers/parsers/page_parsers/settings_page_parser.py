from __future__ import annotations


__all__ = ('SettingsPageParser', 'SettingsPageParsingOptions')


from dataclasses import dataclass

from funpayparsers.types import Settings
from funpayparsers.types.pages import SettingsPage
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)


@dataclass(frozen=True)
class SettingsPageParsingOptions(ParsingOptions):
    """Options class for ``SettingsPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``ProfilePageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``ProfilePageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """


class SettingsPageParser(FunPayHTMLObjectParser[SettingsPage, SettingsPageParsingOptions]):
    """
    Class for parsing user settings page (`https://funpay.com/account/settings`).
    """

    def _parse(self) -> SettingsPage:
        header = PageHeaderParser(
            self.tree.css_first('header').html or '',
            options=self.options.page_header_parsing_options,
        ).parse()

        settings_list = self.tree.css_first('div.setting-list')

        settings_groups = settings_list.css('div.setting-group')

        notifications = {}
        telegram_username = None
        offers_hidden = None

        notifications_block = settings_groups[-1]
        for button in notifications_block.css('button.btn-notice-channel'):
            if button.attributes['data-channel'] == '3' and 'disabled' not in button.attributes:
                telegram_username = button.parent.parent.css_first('b').text(strip=True)[1:]

            notifications[button.attributes['data-channel']] = (
                button.attributes['data-active'] == '1'
            )

        offers_hiding_block = None if not header.sales_available else settings_groups[-2]

        if offers_hiding_block:
            radio_item = offers_hiding_block.css_first('li.megaswitch-radio.active')
            offers_hidden = radio_item.attributes['data-value'] == '1'

        return SettingsPage(
            raw_source=self.raw_source,
            header=header,
            app_data=AppDataParser(
                self.tree.css_first('body').attributes['data-app-data'] or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            settings=Settings(
                raw_source=settings_list.html or '',
                telegram_username=telegram_username,
                telegram_notifications=notifications['3'],
                push_notifications=notifications['1'],
                email_notifications=notifications['2'],
                offers_hidden=offers_hidden,
            ),
        )
