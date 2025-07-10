from __future__ import annotations


__all__ = (
    'Currency',
    'OrderStatus',
    'PaymentMethod',
    'SubcategoryType',
    'TransactionStatus',
    'BadgeType',
    'UpdateType',
    'Language',
)


import re
from typing import Type, TypeVar
from enum import UNIQUE, Enum, verify
from types import MappingProxyType
from functools import cache


T = TypeVar('T')


@verify(UNIQUE)
class UpdateType(Enum):
    ORDERS_COUNTERS = 'orders_counters'
    CHAT_COUNTER = 'chat_counter'
    CHAT_BOOKMARKS = 'chat_bookmarks'
    CHAT_NODE = 'chat_node'
    CPU = 'c-p-u'

    @classmethod
    def get_by_type_str(cls: Type[T], type_str: str, /) -> T | None:
        """Determine an update type by its type string."""
        if type_str not in cls:
            return None
        return cls(type_str)


@verify(UNIQUE)
class SubcategoryType(Enum):
    """Subcategory types enumerations."""

    COMMON = 'lot'
    """Common lots."""

    CURRENCY = 'chip'
    """Currency lots (/chips/)."""

    UNKNOWN = ''
    """Unknown type. Just in case, for future FunPay updates."""

    @classmethod
    def get_by_url(cls: Type[T], url: str, /) -> T:
        """
        Determine a subcategory type by URL.
        """
        for i in cls:
            if i is cls.UNKNOWN:
                continue
            if i.value in url:
                return i
        return cls.UNKNOWN


@verify(UNIQUE)
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

    @classmethod
    def get_by_css_class(cls: Type[T], css_class: str, /) -> T:
        """
        Determine the order status based on a given CSS class string.
        """
        for i in cls:
            if i is cls.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return cls.UNKNOWN


@verify(UNIQUE)
class Currency(Enum):
    """Currencies enumeration."""

    UNKNOWN = ''
    """Unknown currency. Just in case, for future FunPay updates."""

    RUB = '₽'
    USD = '$'
    EUR = '€'

    @classmethod
    def get_by_character(cls: Type[T], character: str, /) -> T:
        """Determine the currency based on a given currency string."""
        if character not in cls:
            return cls.UNKNOWN
        return cls(character)


@verify(UNIQUE)
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

    @classmethod
    def get_by_css_class(cls: Type[T], css_class: str, /) -> T:
        """
        Determine the transaction type based on a given CSS class string.
        """

        for i in cls:
            if i is cls.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return cls.UNKNOWN


@verify(UNIQUE)
class SystemMessageType(Enum): ...


@verify(UNIQUE)
class BadgeType(Enum):
    """Badge types enumeration."""

    BANNED = 'label-danger'
    NOTIFICATIONS = 'label-primary'
    SUPPORT = 'label-success'
    AUTO_DELIVERY = 'label-default'
    UNKNOWN = ''

    @classmethod
    def get_by_css_class(cls: Type[T], css_class: str, /) -> T:
        """
        Determine the badge type based on a given CSS class string.
        """
        for i in cls:
            if i is cls.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return cls.UNKNOWN


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

    @classmethod
    @cache
    def css_class_to_method_map(cls: Type[T]) -> MappingProxyType[str, T]:
        return MappingProxyType(
            {css_class: method for method in cls for css_class in method.value}
        )

    @classmethod
    def get_by_css_class(cls: Type[T], css_class: str) -> T:
        """Determine the payment method based on a given CSS class string."""
        match = _PAYMENT_METHOD_CLS_RE.search(css_class)
        if not match:
            return cls.UNKNOWN

        css_class = match.string[match.start() : match.end()]
        return cls.css_class_to_method_map().get(css_class) or cls.UNKNOWN


class Language(Enum):
    """Page languages enumeration."""

    UNKNOWN = ''
    RU = 'ru'
    EN = 'en'
    UK = 'uk'

    @classmethod
    def get_by_lang_code(cls: Type[T], lang_code: str, /) -> T:
        if lang_code not in cls:
            return cls.UNKNOWN
        return cls(lang_code)
