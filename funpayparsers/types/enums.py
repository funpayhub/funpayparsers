from __future__ import annotations


__all__ = (
    'Currency',
    'OrderStatus',
    'PaymentMethod',
    'SubcategoryType',
    'TransactionStatus',
    'BadgeType',
    'RunnerDataType',
    'Language',
    'MessageType',
)


import re
from typing import Any
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from functools import cache

from funpayparsers import message_type_re as msg_re


class RunnerDataType(Enum):
    """Runner data types enumeration."""

    ORDERS_COUNTERS = 'orders_counters'
    """Orders counters data."""

    CHAT_COUNTER = 'chat_counter'
    """Chat counter data."""

    CHAT_BOOKMARKS = 'chat_bookmarks'
    """Chat bookmarks data."""

    CHAT_NODE = 'chat_node'
    """Chat node data."""

    CPU = 'c-p-u'
    """Currently viewing offer info."""

    @staticmethod
    def get_by_type_str(type_str: str, /) -> RunnerDataType | None:
        """Determine an update type by its type string."""
        for i in RunnerDataType:
            if i.value == type_str:
                return i
        return None


@dataclass(frozen=True)
class _SubcategoryTypeAliases:
    url_alias: str
    showcase_alias: str


class SubcategoryType(Enum):
    """Subcategory types enumerations."""

    COMMON = _SubcategoryTypeAliases('lots', 'lot')
    """Common lots."""

    CURRENCY = _SubcategoryTypeAliases('chips', 'chip')
    """Currency lots (/chips/)."""

    UNKNOWN = _SubcategoryTypeAliases('', '')
    """Unknown type. Just in case, for future FunPay updates."""

    @staticmethod
    def get_by_url(url: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by URL.
        """
        for i in SubcategoryType:
            if i is SubcategoryType.UNKNOWN:
                continue
            if i.value.url_alias in url:
                return i
        return SubcategoryType.UNKNOWN

    @staticmethod
    def get_by_showcase_data_section(showcase_data_section: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by showcase data section value.
        """
        for i in SubcategoryType:
            if i is SubcategoryType.UNKNOWN:
                continue
            if i.value.showcase_alias in showcase_data_section:
                return i
        return SubcategoryType.UNKNOWN


class OrderStatus(Enum):
    """
    Order statuses enumeration.

    Each value is a css class, that identifies order status.
    """

    PAID = 'text-primary'
    """Paid, but not COMPLETED order."""

    COMPLETED = 'text-success'
    """Completed order."""

    REFUNDED = 'text-warning'
    """Refunded order."""

    UNKNOWN = ''
    """Unknown status. Just in case, for future FunPay updates."""

    @staticmethod
    def get_by_css_class(css_class: str, /) -> OrderStatus:
        """
        Determine the order status based on a given CSS class string.
        """
        for i in OrderStatus:
            if i is OrderStatus.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return OrderStatus.UNKNOWN


class Currency(Enum):
    """Currencies enumeration."""

    UNKNOWN = ''
    """Unknown currency. Just in case, for future FunPay updates."""

    RUB = '₽'
    USD = '$'
    EUR = '€'

    @staticmethod
    def get_by_character(character: str, /) -> Currency:
        """Determine the currency based on a given currency string."""
        for i in Currency:
            if i.value == character:
                return i
        return Currency.UNKNOWN


class TransactionStatus(Enum):
    """Transaction statuses enumeration."""

    PENDING = 'transaction-status-waiting'
    """Pending transaction."""

    COMPLETED = 'transaction-status-complete'
    """Completed transaction."""

    CANCELLED = 'transaction-status-cancel'
    """Cancelled transaction."""

    UNKNOWN = ''
    """Unknown transaction status. Just in case, for future FunPay updates."""

    @staticmethod
    def get_by_css_class(css_class: str, /) -> TransactionStatus:
        """
        Determine the transaction type based on a given CSS class string.
        """

        for i in TransactionStatus:
            if i is TransactionStatus.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return TransactionStatus.UNKNOWN


class MessageType(Enum):
    NON_SYSTEM = 'NON_SYSTEM'
    UNKNOWN_SYSTEM = 'UNKNOWN_SYSTEM'
    NEW_ORDER = msg_re.NEW_ORDER
    ORDER_CLOSED = msg_re.ORDER_CLOSED
    ORDER_CLOSED_BY_ADMIN = msg_re.ORDER_CLOSED_BY_ADMIN
    ORDER_REOPENED = msg_re.ORDER_REOPENED
    ORDER_REFUNDED = msg_re.ORDER_REFUNDED
    ORDER_PARTIALLY_REFUNDED = msg_re.ORDER_PARTIALLY_REFUND
    NEW_FEEDBACK = msg_re.NEW_FEEDBACK
    FEEDBACK_CHANGED = msg_re.FEEDBACK_CHANGED
    FEEDBACK_DELETED = msg_re.FEEDBACK_DELETED
    NEW_FEEDBACK_REPLY = msg_re.NEW_FEEDBACK_REPLY
    FEEDBACK_REPLY_CHANGED = msg_re.FEEDBACK_REPLY_CHANGED
    FEEDBACK_REPLY_DELETED = msg_re.FEEDBACK_REPLY_DELETED

    @staticmethod
    def get_by_message_text(message_text: str, /) -> MessageType:
        for i in MessageType:
            if isinstance(i.value, str):
                continue

            if i.value.fullmatch(message_text):
                return i

        return MessageType.NON_SYSTEM


class BadgeType(Enum):
    """Badge types enumeration."""

    BANNED = 'label-danger'
    NOTIFICATIONS = 'label-primary'
    SUPPORT = 'label-success'
    AUTO_DELIVERY = 'label-default'
    NOT_ACTIVATED = 'label-warning'
    UNKNOWN = ''

    @staticmethod
    def get_by_css_class(css_class: str, /) -> BadgeType:
        """
        Determine the badge type based on a given CSS class string.
        """
        for i in BadgeType:
            if i is BadgeType.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return BadgeType.UNKNOWN


_PAYMENT_METHOD_CLS_RE = re.compile(r'payment-method-[a-zA-Z0-9_]+')


class PaymentMethod(Enum):
    """
    Enumeration of payment methods (withdrawal / deposit types).

    Based on:
        - Sprites: https://funpay.com/16/img/layout/sprites.min.png
        (resized to 405px in auto mode)
        - CSS: https://funpay.com/687/css/main.css
    """

    QIWI = ('payment-method-1', 'payment-method-qiwi')
    """
    Qiwi wallett payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=94``.
    """

    YANDEX = ('payment-method-2', 'payment-method-yandex', 'payment-method-fps')
    """
    Yandex payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=34``.
    """

    FPS = ('payment-method-21',)
    """
    FPS (what) payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=364``.
    """

    WEBMONEY_WME = ('payment-method-3', 'payment-method-wme')
    """
    WebMoney WME payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMP = ('payment-method-4', 'payment-method-wmp')
    """
    WebMoney WMP payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMR = ('payment-method-5', 'payment-method-wmr')
    """
    WebMoney WMR payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMZ = ('payment-method-6', 'payment-method-wmz')
    """
    WebMoney WMZ payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_UNKNOWN = ('payment-method-10',)
    """
    WebMoney unknown type. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    CARD_RUB = ('payment-method-7', 'payment-method-card_rub')
    """
    Card RUB payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_USD = ('payment-method-card_usd',)
    """
    Card USD payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_EUR = ('payment-method-card_eur',)
    """
    Card EUR payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_UAH = ('payment-method-card_uah',)
    """
    Card UAH payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_UNKNOWN = (
        'payment-method-11',
        'payment-method-15',
        'payment-method-16',
        'payment-method-25',
        'payment-method-26',
        'payment-method-27',
        'payment-method-32',
        'payment-method-33',
        'payment-method-34',
        'payment-method-35',
        'payment-method-37',
        'payment-method-38',
        'payment-method-39',
        'payment-method-40',
    )
    """
    Unknown card, maybe it will added soon. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    MOBILE = ('payment-method-8',)
    """
    Mobile payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=124``.
    """

    APPLE = ('payment-method-9', 'payment-method-19', 'payment-method-20')
    """
    Apple Pay payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=154``.
    """

    MASTERCARD = ('payment-method-12', 'payment-method-22', 'payment-method-23')
    """
    MasterCard payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=274``.
    """

    VISA = ('payment-method-13', 'payment-method-28', 'payment-method-29')
    """
    Visa payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=304``.
    """

    GOOGLE = ('payment-method-14', 'payment-method-17', 'payment-method-18')
    """
    Google Pay payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=244``.
    """

    FUNPAY = ('payment-method-24',)
    """
    FunPay balance payment method.
    
    You can pay from your balance if the funds remain on your balance for
    48 hours from the moment of receipt, or if you have an instant withdraw.
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=214``.
    """

    LITECOIN = ('payment-method-30',)
    """
    Litecoin (LTC) payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=4``.
    """

    BINANCE = ('payment-method-31',)
    """
    Binance generic payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    BINANCE_USDT = ('payment-method-binance_usdt',)
    """
    Binance USDT payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    BINANCE_USDC = ('payment-method-binance_usdc',)
    """
    Binance USDC payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    PAYPAL = ('payment-method-36', 'payment-method-paypal')
    """
    PayPal payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=184``.
    """

    USDT_TRC = ('payment-method-usdt_trc',)
    """
    USDT TRC-20 payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=64``.
    """

    UNKNOWN = ('',)
    """Unknown payment method."""

    # MIR = 26, ('UNKNOWN', ), (345, Y)  =(

    @staticmethod
    @cache
    def css_class_to_method_map() -> MappingProxyType[str, PaymentMethod]:
        return MappingProxyType(
            {css_class: method for method in PaymentMethod for css_class in method.value}
        )

    @staticmethod
    def get_by_css_class(css_class: str, /) -> PaymentMethod:
        """Determine the payment method based on a given CSS class string."""
        match = _PAYMENT_METHOD_CLS_RE.search(css_class)
        if not match:
            return PaymentMethod.UNKNOWN

        css_class = match.string[match.start() : match.end()]
        return PaymentMethod.css_class_to_method_map().get(css_class) or PaymentMethod.UNKNOWN


@dataclass(frozen=True)
class _LanguageAliases:
    appdata_alias: str
    url_alias: str
    header_menu_css_class: str


class Language(Enum):
    """Page languages enumeration."""

    UNKNOWN = _LanguageAliases('', '', '')
    RU = _LanguageAliases('ru', '', 'menu-icon-lang-ru')
    EN = _LanguageAliases('en', 'en', 'menu-icon-lang-en')
    UK = _LanguageAliases('uk', 'uk', 'menu-icon-lang-uk')

    @staticmethod
    def get_by_lang_code(lang_code: Any, /) -> Language:
        for i in Language:
            if i is Language.UNKNOWN:
                continue

            if i.value.appdata_alias == lang_code:
                return i
        return Language.UNKNOWN

    @staticmethod
    def get_by_header_menu_css_class(css_class: str, /) -> Language:
        for i in Language:
            if i is Language.UNKNOWN:
                continue

            if i.value.header_menu_css_class in css_class:
                return i
        return Language.UNKNOWN
