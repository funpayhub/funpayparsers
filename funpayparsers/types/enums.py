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
import warnings

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
        warnings.warn(
            '`RunnerDataType.get_by_type_str` is deprecated. '
            'Use `RunnerDataType.from_type_str` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return RunnerDataType.from_type_str(type_str)

    @classmethod
    def from_type_str(cls, type_str: str, /) -> RunnerDataType | None:
        """Determine an update type by its type string."""
        data = {
            'orders_counters': RunnerDataType.ORDERS_COUNTERS,
            'chat_counter': RunnerDataType.CHAT_COUNTER,
            'chat_bookmarks': RunnerDataType.CHAT_BOOKMARKS,
            'chat_node': RunnerDataType.CHAT_NODE,
            'c-p-u': RunnerDataType.CPU
        }
        return data.get(type_str.lower())


@dataclass(frozen=True)
class _SubcategoryTypeAliases:
    url_alias: str
    showcase_alias: str


class SubcategoryType(Enum):
    """Subcategory types enumerations."""

    OFFERS = 'OFFERS'
    """Common lots."""

    CHIPS = 'CHIPS'
    """Currency lots (/chips/)."""

    UNKNOWN = 'UNKNOWN'
    """Unknown type. Just in case, for future FunPay updates."""

    @staticmethod
    def get_by_url(url: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by URL.
        """
        warnings.warn(
            '`SubcategoryType.get_by_url` is deprecated. Use `SubcategoryType.from_url` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return SubcategoryType.from_url(url)

    @staticmethod
    def get_by_showcase_data_section(showcase_data_section: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by showcase data section value.
        """
        warnings.warn(
            '`SubcategoryType.get_by_showcase_data_section` is deprecated. '
            'Use `SubcategoryType.from_showcase_data_section` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return SubcategoryType.from_showcase_data_section(showcase_data_section)

    @classmethod
    def from_url(cls, url: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by URL.
        """
        for i in SubcategoryType:
            if i is SubcategoryType.UNKNOWN:
                continue
            if _SUBCATEGORY_TYPE_ALIASES[i].url_alias in url:
                return i
        return SubcategoryType.UNKNOWN

    @classmethod
    def from_showcase_data_section(cls, showcase_data_section: str, /) -> SubcategoryType:
        for i in SubcategoryType:
            if i is SubcategoryType.UNKNOWN:
                continue
            if _SUBCATEGORY_TYPE_ALIASES[i].showcase_alias in showcase_data_section:
                return i
        return SubcategoryType.UNKNOWN


    @property
    def COMMON(self) -> SubcategoryType:
        warnings.warn(
            '`SubcategoryType.COMMON` is deprecated. Use `SubcategoryType.OFFERS` instead.',
            DeprecationWarning
        )
        return self.OFFERS

    @property
    def CURRENCY(self) -> SubcategoryType:
        warnings.warn(
            '`SubcategoryType.CURRENCY` is deprecated. Use `SubcategoryType.CHIPS` instead.',
            DeprecationWarning
        )
        return self.CHIPS

_SUBCATEGORY_TYPE_ALIASES = {
    SubcategoryType.OFFERS: _SubcategoryTypeAliases('lots', 'lot'),
    SubcategoryType.CHIPS: _SubcategoryTypeAliases('chips', 'chip')
}


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
        if character == '¤':
            return Currency.RUB

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
    NEW_ORDER = 'NEW_ORDER'
    ORDER_CLOSED = 'ORDER_CLOSED'
    ORDER_CLOSED_BY_ADMIN = 'ORDER_CLOSED_BY_ADMIN'
    ORDER_REOPENED = 'ORDER_REOPENED'
    ORDER_REFUNDED = 'ORDER_REFUNDED'
    ORDER_PARTIALLY_REFUNDED = 'ORDER_PARTIALLY_REFUND'
    NEW_FEEDBACK = 'NEW_FEEDBACK'
    FEEDBACK_CHANGED = 'FEEDBACK_CHANGED'
    FEEDBACK_DELETED = 'FEEDBACK_DELETED'
    NEW_FEEDBACK_REPLY = 'NEW_FEEDBACK_REPLY'
    FEEDBACK_REPLY_CHANGED = 'FEEDBACK_REPLY_CHANGED'
    FEEDBACK_REPLY_DELETED = 'FEEDBACK_REPLY_DELETED'

    @staticmethod
    def get_by_message_text(message_text: str, /) -> MessageType:
        warnings.warn(
            '`MessageType.get_by_message_text` is deprecated. '
            'Use `MessageType.from_message_text` instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return MessageType.from_message_text(message_text)

    @classmethod
    def from_message_text(cls, message_text: str, /) -> MessageType:
        for t, regexp in _MESSAGE_RE.items():
            if regexp.fullmatch(message_text):
                return t
        return MessageType.NON_SYSTEM

_MESSAGE_RE = {
    MessageType.NEW_ORDER: msg_re.NEW_ORDER,
    MessageType.ORDER_CLOSED: msg_re.ORDER_CLOSED,
    MessageType.ORDER_CLOSED_BY_ADMIN: msg_re.ORDER_CLOSED_BY_ADMIN,
    MessageType.ORDER_REOPENED: msg_re.ORDER_REOPENED,
    MessageType.ORDER_REFUNDED: msg_re.ORDER_REFUNDED,
    MessageType.ORDER_PARTIALLY_REFUNDED: msg_re.ORDER_PARTIALLY_REFUND,
    MessageType.NEW_FEEDBACK: msg_re.NEW_FEEDBACK,
    MessageType.FEEDBACK_CHANGED: msg_re.FEEDBACK_CHANGED,
    MessageType.FEEDBACK_DELETED: msg_re.FEEDBACK_DELETED,
    MessageType.NEW_FEEDBACK_REPLY: msg_re.NEW_FEEDBACK_REPLY,
    MessageType.FEEDBACK_REPLY_CHANGED: msg_re.FEEDBACK_REPLY_CHANGED,
    MessageType.FEEDBACK_REPLY_DELETED: msg_re.FEEDBACK_REPLY_DELETED,
}


class BadgeType(Enum):
    """Badge types enumeration."""

    BANNED = 'BANNED'
    NOTIFICATIONS = 'NOTIFICATIONS'
    SUPPORT = 'SUPPORT'
    AUTO_DELIVERY = 'AUTO_DELIVERY'
    NOT_ACTIVATED = 'NOT_ACTIVATED'
    UNKNOWN = 'UNKNOWN'

    @staticmethod
    def get_by_css_class(css_class: str, /) -> BadgeType:
        """
        Determine the badge type based on a given CSS class string.
        """
        warnings.warn(
            '`BadgeType.get_by_css_class` is deprecated. '
            'Use `BadgeType.from_css_class` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return BadgeType.from_css_class(css_class)

    @classmethod
    def from_css_class(cls, css_class: str, /) -> BadgeType:
        """
        Determine the badge type based on a given CSS class string.
        """
        data = {
            'label-danger': BadgeType.BANNED,
            'label-primary': BadgeType.NOTIFICATIONS,
            'label-success': BadgeType.SUPPORT,
            'label-default': BadgeType.AUTO_DELIVERY,
            'label-warning': BadgeType.NOT_ACTIVATED,
        }
        for k, v in data.items():
            if k in css_class:
                return v
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

    QIWI = 'QIWI'
    """
    Qiwi wallett payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=94``.
    """

    YANDEX = 'YANDEX'
    """
    Yandex payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=34``.
    """

    FPS = 'FPS'
    """
    FPS (what) payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=364``.
    """

    WEBMONEY_WME = 'WEBMONEY_WME'
    """
    WebMoney WME payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMP = 'WEBMONEY_WMP'
    """
    WebMoney WMP payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMR = 'WEBMONEY_WMR'
    """
    WebMoney WMR payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMZ = 'WEBMONEY_WMZ'
    """
    WebMoney WMZ payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_UNKNOWN = 'WEBMONEY_UNKNOWN'
    """
    WebMoney unknown type. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    CARD_RUB = 'CARD_RUB'
    """
    Card RUB payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_USD = 'CARD_USD'
    """
    Card USD payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_EUR = 'CARD_EUR'
    """
    Card EUR payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_UAH = 'CARD_UAH'
    """
    Card UAH payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_UNKNOWN = 'CARD_UNKNOWN'
    """
    Unknown card, maybe it will added soon. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    MOBILE = 'MOBILE'
    """
    Mobile payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=124``.
    """

    APPLE = 'APPLE'
    """
    Apple Pay payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=154``.
    """

    MASTERCARD = 'MASTERCARD'
    """
    MasterCard payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=274``.
    """

    VISA = 'VISA'
    """
    Visa payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=304``.
    """

    GOOGLE = 'GOOGLE'
    """
    Google Pay payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=244``.
    """

    FUNPAY = 'FUNPAY'
    """
    FunPay balance payment method.
    
    You can pay from your balance if the funds remain on your balance for
    48 hours from the moment of receipt, or if you have an instant withdraw.
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=214``.
    """

    LITECOIN = 'LITECOIN'
    """
    Litecoin (LTC) payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=4``.
    """

    BINANCE = 'BINANCE'
    """
    Binance generic payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    BINANCE_USDT = 'BINANCE_USDT'
    """
    Binance USDT payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    BINANCE_USDC = 'BINANCE_USDC'
    """
    Binance USDC payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    PAYPAL = 'PAYPAL'
    """
    PayPal payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=184``.
    """

    USDT_TRC = 'USDT_TRC'
    """
    USDT TRC-20 payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=64``.
    """

    UNKNOWN = 'UNKNOWN'
    """Unknown payment method."""

    # MIR = 26, ('UNKNOWN', ), (345, Y)  =(

    @staticmethod
    def get_by_css_class(css_class: str, /) -> PaymentMethod:
        """Determine the payment method based on a given CSS class string."""
        warnings.warn(
            '`PaymentMethod.get_by_css_class` is deprecated. '
            'Use `PaymentMethod.from_css_class` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return PaymentMethod.from_css_class(css_class)

    @classmethod
    def from_css_class(cls, css_class: str, /) -> PaymentMethod:
        """Determine the payment method based on a given CSS class string."""
        match = _PAYMENT_METHOD_CLS_RE.search(css_class)
        if not match:
            return PaymentMethod.UNKNOWN

        css_class = match.group()
        return _CSS_CLASS_TO_PAYMENT_METHOD.get(css_class, PaymentMethod.UNKNOWN)


_PAYMENT_METHODS = {
    PaymentMethod.QIWI: ('payment-method-1', 'payment-method-qiwi'),
    PaymentMethod.YANDEX: ('payment-method-2', 'payment-method-yandex', 'payment-method-fps'),
    PaymentMethod.FPS: ('payment-method-21',),
    PaymentMethod.WEBMONEY_WME: ('payment-method-3', 'payment-method-wme'),
    PaymentMethod.WEBMONEY_WMP: ('payment-method-4', 'payment-method-wmp'),
    PaymentMethod.WEBMONEY_WMR: ('payment-method-5', 'payment-method-wmr'),
    PaymentMethod.WEBMONEY_WMZ: ('payment-method-6', 'payment-method-wmz'),
    PaymentMethod.WEBMONEY_UNKNOWN: ('payment-method-10',),
    PaymentMethod.CARD_RUB: ('payment-method-7', 'payment-method-card_rub'),
    PaymentMethod.CARD_USD: ('payment-method-card_usd',),
    PaymentMethod.CARD_EUR: ('payment-method-card_eur',),
    PaymentMethod.CARD_UAH: ('payment-method-card_uah',),
    PaymentMethod.CARD_UNKNOWN: (
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
    ),
    PaymentMethod.MOBILE: ('payment-method-8',),
    PaymentMethod.APPLE: ('payment-method-9', 'payment-method-19', 'payment-method-20'),
    PaymentMethod.MASTERCARD: ('payment-method-12', 'payment-method-22', 'payment-method-23'),
    PaymentMethod.VISA: ('payment-method-13', 'payment-method-28', 'payment-method-29'),
    PaymentMethod.GOOGLE: ('payment-method-14', 'payment-method-17', 'payment-method-18'),
    PaymentMethod.FUNPAY: ('payment-method-24',),
    PaymentMethod.LITECOIN: ('payment-method-30',),
    PaymentMethod.BINANCE: ('payment-method-31',),
    PaymentMethod.BINANCE_USDT: ('payment-method-binance_usdt',),
    PaymentMethod.BINANCE_USDC: ('payment-method-binance_usdc',),
    PaymentMethod.PAYPAL: ('payment-method-36', 'payment-method-paypal'),
    PaymentMethod.USDT_TRC: ('payment-method-usdt_trc',),
}

_CSS_CLASS_TO_PAYMENT_METHOD = {
    css: enm for enm, classes in _PAYMENT_METHODS.items() for css in classes
}


class Language(Enum):
    """Page languages enumeration."""

    UNKNOWN = 'UNKNOWN'
    RU = 'RU'
    EN = 'EN'
    UK = 'UK'

    @staticmethod
    def get_by_lang_code(lang_code: Any, /) -> Language:
        warnings.warn(
            '`Language.get_by_lang_code` is deprecated. Use `Language.from_lang_code` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return Language.from_lang_code(lang_code)

    @staticmethod
    def get_by_header_menu_css_class(css_class: str, /) -> Language:
        warnings.warn(
            '`Language.get_by_header_menu_css_class` is deprecated. '
            'Use `Language.from_header_menu_css_class` instead.',
            DeprecationWarning,
            stacklevel=2
        )
        return Language.from_header_menu_css_class(css_class)

    @classmethod
    def from_lang_code(cls, lang_code: str, /) -> Language:
        for i in Language:
            if i is Language.UNKNOWN:
                continue

            if lang_code == _LANGUAGE_ALIASES[i].appdata_alias:
                return i
        return Language.UNKNOWN

    @classmethod
    def from_header_menu_css_class(cls, css_class: str, /) -> Language:
        for i in Language:
            if i is Language.UNKNOWN:
                continue

            if _LANGUAGE_ALIASES[i].header_menu_css_class in css_class:
                return i
        return Language.UNKNOWN

    @property
    def url_alias(self) -> str:
        return _LANGUAGE_ALIASES[self].url_alias

    @property
    def appdata_alias(self) -> str:
        return _LANGUAGE_ALIASES[self].appdata_alias

    @property
    def header_menu_css_class(self) -> str:
        return _LANGUAGE_ALIASES[self].header_menu_css_class


@dataclass(frozen=True)
class _LanguageAliases:
    appdata_alias: str
    url_alias: str
    header_menu_css_class: str


_LANGUAGE_ALIASES = {
    Language.UNKNOWN: _LanguageAliases('', '', ''),
    Language.RU: _LanguageAliases('ru', '', 'menu-icon-lang-ru'),
    Language.EN: _LanguageAliases('en', 'en', 'menu-icon-lang-en'),
    Language.UK: _LanguageAliases('uk', 'uk', 'menu-icon-lang-uk'),
}