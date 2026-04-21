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
    'SubcategoryFieldType',
)


import re
from dataclasses import dataclass
from enum import Enum, auto

from funpayparsers import message_type_re as msg_re


class RunnerDataType(Enum):
    """Runner data types enumeration."""

    ORDERS_COUNTERS = auto()
    """Orders counters data."""

    CHAT_COUNTER = auto()
    """Chat counter data."""

    CHAT_BOOKMARKS = auto()
    """Chat bookmarks data."""

    CHAT_NODE = auto()
    """Chat node data."""

    CPU = auto()
    """Currently viewing offer info."""

    @classmethod
    def from_type_str(cls, type_str: str, /) -> RunnerDataType | None:
        """Determine an update type by its type string."""
        data = {
            'orders_counters': RunnerDataType.ORDERS_COUNTERS,
            'chat_counter': RunnerDataType.CHAT_COUNTER,
            'chat_bookmarks': RunnerDataType.CHAT_BOOKMARKS,
            'chat_node': RunnerDataType.CHAT_NODE,
            'c-p-u': RunnerDataType.CPU,
        }
        return data.get(type_str.lower())


class SubcategoryType(Enum):
    """Subcategory types enumerations."""

    OFFERS = auto()
    """Common lots."""

    CHIPS = auto()
    """Currency lots (/chips/)."""

    UNKNOWN = auto()
    """Unknown type. Just in case, for future FunPay updates."""

    @classmethod
    def from_url(cls, url: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by URL.
        """
        for enm, alias in _SUBCATEGORY_TYPE_ALIASES.items():
            if alias.url_alias in url.lower():
                return enm
        return SubcategoryType.UNKNOWN

    @classmethod
    def from_showcase_data_section(cls, showcase_data_section: str, /) -> SubcategoryType:
        """
        Determine a subcategory type by showcase data section value.
        """
        for enm, alias in _SUBCATEGORY_TYPE_ALIASES.items():
            if alias.showcase_alias in showcase_data_section.lower():
                return enm
        return SubcategoryType.UNKNOWN

    @property
    def url_alias(self) -> str:
        return _SUBCATEGORY_TYPE_ALIASES[self].url_alias

    @property
    def showcase_alias(self) -> str:
        return _SUBCATEGORY_TYPE_ALIASES[self].showcase_alias


@dataclass(frozen=True)
class _SubcategoryTypeAliases:
    url_alias: str
    showcase_alias: str


_SUBCATEGORY_TYPE_ALIASES = {
    SubcategoryType.OFFERS: _SubcategoryTypeAliases('lots', 'lot'),
    SubcategoryType.CHIPS: _SubcategoryTypeAliases('chips', 'chip'),
    SubcategoryType.UNKNOWN: _SubcategoryTypeAliases('', ''),
}


class OrderStatus(Enum):
    """
    Order statuses enumeration.

    Each value is a css class, that identifies order status.
    """

    PAID = auto()
    """Paid, but not COMPLETED order."""

    COMPLETED = auto()
    """Completed order."""

    REFUNDED = auto()
    """Refunded order."""

    UNKNOWN = auto()
    """Unknown status. Just in case, for future FunPay updates."""

    @classmethod
    def from_css_class(cls, css_class: str, /) -> OrderStatus:
        """
        Determine the order status based on a given CSS class string.
        """
        for css, enm in _ORDER_STATUSES.items():
            if css in css_class.lower():
                return enm
        return OrderStatus.UNKNOWN


_ORDER_STATUSES = {
    'text-primary': OrderStatus.PAID,
    'text-success': OrderStatus.COMPLETED,
    'text-warning': OrderStatus.REFUNDED,
}


class Currency(Enum):
    """Currencies enumeration."""

    UNKNOWN = auto()
    """Unknown currency. Just in case, for future FunPay updates."""

    RUB = auto()
    USD = auto()
    EUR = auto()

    @classmethod
    def from_character(cls, character: str, /) -> Currency:
        """Determine the currency based on a given currency string."""
        return _CURRENCIES.get(character, Currency.UNKNOWN)


_CURRENCIES = {
    '₽': Currency.RUB,
    '$': Currency.USD,
    '€': Currency.EUR,
    '¤': Currency.RUB,
}


class TransactionStatus(Enum):
    """Transaction statuses enumeration."""

    PENDING = auto()
    """Pending transaction."""

    COMPLETED = auto()
    """Completed transaction."""

    CANCELLED = auto()
    """Cancelled transaction."""

    UNKNOWN = auto()
    """Unknown transaction status. Just in case, for future FunPay updates."""

    @classmethod
    def from_css_class(cls, css_class: str, /) -> TransactionStatus:
        """
        Determine the transaction type based on a given CSS class string.
        """
        for css, enm in _TRANSACTION_STATUSES.items():
            if css in css_class.lower():
                return enm
        return TransactionStatus.UNKNOWN


_TRANSACTION_STATUSES = {
    'transaction-status-waiting': TransactionStatus.PENDING,
    'transaction-status-complete': TransactionStatus.COMPLETED,
    'transaction-status-cancel': TransactionStatus.CANCELLED,
}


class MessageType(Enum):
    NON_SYSTEM = auto()
    UNKNOWN_SYSTEM = auto()
    NEW_ORDER = auto()
    ORDER_CLOSED = auto()
    ORDER_CLOSED_BY_ADMIN = auto()
    ORDER_REOPENED = auto()
    ORDER_REFUNDED = auto()
    ORDER_PARTIALLY_REFUNDED = auto()
    NEW_FEEDBACK = auto()
    FEEDBACK_CHANGED = auto()
    FEEDBACK_DELETED = auto()
    NEW_FEEDBACK_REPLY = auto()
    FEEDBACK_REPLY_CHANGED = auto()
    FEEDBACK_REPLY_DELETED = auto()

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

    BANNED = auto()
    NOTIFICATIONS = auto()
    SUPPORT = auto()
    AUTO_DELIVERY = auto()
    NOT_ACTIVATED = auto()
    UNKNOWN = auto()

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

    QIWI = auto()
    """
    Qiwi wallett payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=94``.
    """

    YANDEX = auto()
    """
    Yandex payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=34``.
    """

    FPS = auto()
    """
    FPS (what) payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=364``.
    """

    WEBMONEY_WME = auto()
    """
    WebMoney WME payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMP = auto()
    """
    WebMoney WMP payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMR = auto()
    """
    WebMoney WMR payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_WMZ = auto()
    """
    WebMoney WMZ payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    WEBMONEY_UNKNOWN = auto()
    """
    WebMoney unknown type. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=64``.
    """

    CARD_RUB = auto()
    """
    Card RUB payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_USD = auto()
    """
    Card USD payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_EUR = auto()
    """
    Card EUR payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_UAH = auto()
    """
    Card UAH payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    CARD_UNKNOWN = auto()
    """
    Unknown card, maybe it will added soon. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=4``.
    """

    MOBILE = auto()
    """
    Mobile payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=124``.
    """

    APPLE = auto()
    """
    Apple Pay payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=154``.
    """

    MASTERCARD = auto()
    """
    MasterCard payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=274``.
    """

    VISA = auto()
    """
    Visa payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=304``.
    """

    GOOGLE = auto()
    """
    Google Pay payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=244``.
    """

    FUNPAY = auto()
    """
    FunPay balance payment method.
    
    You can pay from your balance if the funds remain on your balance for
    48 hours from the moment of receipt, or if you have an instant withdraw.
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=214``.
    """

    LITECOIN = auto()
    """
    Litecoin (LTC) payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=4``.
    """

    BINANCE = auto()
    """
    Binance generic payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    BINANCE_USDT = auto()
    """
    Binance USDT payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    BINANCE_USDC = auto()
    """
    Binance USDC payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=34``.
    """

    PAYPAL = auto()
    """
    PayPal payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=345, y=184``.
    """

    USDT_TRC = auto()
    """
    USDT TRC-20 payment method. 
    
    Sprite coords (see ``PaymentMethod`` doc-string): ``x=375, y=64``.
    """

    UNKNOWN = auto()
    """Unknown payment method."""

    # MIR = 26, ('UNKNOWN', ), (345, Y)  =(

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

    UNKNOWN = auto()
    RU = auto()
    EN = auto()
    UK = auto()

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


class SubcategoryFieldType(Enum):
    """Subcategory field type (from ``data-fields`` JSON ``type`` key)."""

    UNKNOWN = auto()
    """Unknown field type. Returned for unrecognized type integers."""

    NUMERIC_RANGE = auto()
    """Numeric text input, used as a range filter on catalog pages."""

    TEXT = auto()
    """Single-line text input."""

    TEXTAREA = auto()
    """Multi-line textarea."""

    SELECT = auto()
    """Dropdown select with conditional visibility support."""

    DROPDOWN = auto()
    """Plain dropdown select."""

    IMAGES = auto()
    """Image upload field."""

    @classmethod
    def from_type_code(cls, type_code: int, /) -> SubcategoryFieldType:
        """Return the field type corresponding to ``type_code``, or ``UNKNOWN``."""
        return _SUBCATEGORY_FIELD_TYPE_MAP.get(type_code, cls.UNKNOWN)


_SUBCATEGORY_FIELD_TYPE_MAP: dict[int, SubcategoryFieldType] = {
    1: SubcategoryFieldType.NUMERIC_RANGE,
    2: SubcategoryFieldType.TEXT,
    3: SubcategoryFieldType.TEXTAREA,
    4: SubcategoryFieldType.SELECT,
    5: SubcategoryFieldType.DROPDOWN,
    6: SubcategoryFieldType.IMAGES,
}
