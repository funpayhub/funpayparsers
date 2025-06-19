__all__ = (
    'Currency',
    'OrderStatus',
    'PaymentMethod',
    'SubcategoryType',
    'TransactionStatus',
    'BadgeType',
)


from enum import UNIQUE, Enum, StrEnum, verify
from types import MappingProxyType
from functools import cache


@verify(UNIQUE)
class SubcategoryType(StrEnum):
    """
    Subcategory types enumerations.
    """

    COMMON = 'lots'
    """Common lots."""

    CURRENCY = 'chips'
    """Currency lots (/chips/)."""

    UNKNOWN = ''
    """Unknown type. Just in case, for future FunPay updates."""

    @staticmethod
    def get_by_url(url: str, /) -> 'SubcategoryType':
        """
        Determine a subcategory type by URL.
        """
        for i in SubcategoryType:
            if i is SubcategoryType.UNKNOWN:
                continue
            if i.value in url:
                return i
        return SubcategoryType.UNKNOWN


@verify(UNIQUE)
class OrderStatus(StrEnum):
    """
    Order statuses enumeration.

    Each value is a css class, that identifies order status.
    """

    PAID = 'text-primary'
    """Paid, but not completed order."""

    COMPLETED = 'text-success'
    """Completed order."""

    REFUNDED = 'text-warning'
    """Refunded order."""

    UNKNOWN = ''
    """Unknown status. Just in case, for future FunPay updates."""

    @staticmethod
    def get_by_css_class(css_class: str, /) -> 'OrderStatus':
        """
        Determine the order status based on a given CSS class string.

        Examples:
            >>> OrderStatus.get_by_css_class('text-primary some_another_css_class')
            <OrderStatus.PAID: 'text-primary'>

            >>> OrderStatus.get_by_css_class('some_another_css_class text-warning')
            <OrderStatus.REFUNDED: 'text-warning'>

            >>> OrderStatus.get_by_css_class('some_another_css_class text-success')
            <OrderStatus.COMPLETED: 'text-success'>

            >>> OrderStatus.get_by_css_class('some_another_css_class')
            <OrderStatus.UNKNOWN: ''>
        """
        for i in OrderStatus:
            if i is OrderStatus.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return OrderStatus.UNKNOWN


@verify(UNIQUE)
class Currency(StrEnum):
    """Currencies enumeration."""

    UNKNOWN = ''
    """Unknown currency. Just in case, for future FunPay updates."""

    RUB = '₽'
    USD = '$'
    EUR = '€'

    @staticmethod
    def get_by_character(character: str, /) -> 'Currency':
        """
        Determine the currency based on a given currency string.

        Examples:
            >>> Currency.get_by_character('$')
            <Currency.USD: '$'>

            >>> Currency.get_by_character('₽')
            <Currency.RUB: '₽'>

            >>> Currency.get_by_character('€')
            <Currency.EUR: '€'>

            >>> Currency.get_by_character('Amongus')
            <Currency.UNKNOWN: ''>
        """
        for i in Currency:
            if i is Currency.UNKNOWN:
                continue
            if character == i.value:
                return i
        return Currency.UNKNOWN


@verify(UNIQUE)
class TransactionStatus(Enum):
    """Transaction statuses enumeration."""

    pending = 0
    """Pending transaction."""

    completed = 1
    """Completed transaction."""

    cancelled = 2
    """Cancelled transaction."""


@verify(UNIQUE)
class SystemMessageType(Enum): ...


@verify(UNIQUE)
class BadgeType(StrEnum):
    """
    Badge types enumeration.
    """

    BANNED = 'label-danger'
    NOTIFICATIONS = 'label-primary'
    SUPPORT = 'label-success'
    AUTOISSUE = 'label-default'
    UNKNOWN = ''

    @staticmethod
    def get_by_css_class(css_class: str, /) -> 'BadgeType':
        """
        Determine the badge type based on a given CSS class string.

        Examples:
            >>> BadgeType.get_by_css_class('label-danger some_another_css_class')
            <BadgeType.BANNED: 'label-danger'>

            >>> BadgeType.get_by_css_class('some_another_css_class label-primary')
            <BadgeType.NOTIFICATIONS: 'label-primary'>

            >>> BadgeType.get_by_css_class('some_another_css_class')
            <BadgeType.UNKNOWN: ''>
        """
        for i in BadgeType:
            if i is BadgeType.UNKNOWN:
                continue

            if i.value in css_class:
                return i
        return BadgeType.UNKNOWN


class PaymentMethod(Enum):
    """
    Enumeration of payment methods (withdrawal / deposit types).

    Based on:
        - Sprites: https://funpay.com/16/img/layout/sprites.min.png (resized to 405px in auto mode)
        - CSS: https://funpay.com/687/css/main.css
    """

    QIWI = ('payment-method-1', 'payment-method-qiwi')  # 345, 94
    YANDEX = ('payment-method-2', 'payment-method-yandex', 'payment-method-fps')  #345, 34
    FPS = ('payment-method-21',)  # 345, 364

    WEBMONEY_WME = ('payment-method-3', 'payment-method-wme')  # 345, 64
    WEBMONEY_WMP = ('payment-method-4', 'payment-method-wmp')  # 345, 64
    WEBMONEY_WMR = ('payment-method-5', 'payment-method-wmr')  # 345, 64
    WEBMONEY_WMZ = ('payment-method-6', 'payment-method-wmz')  # 345, 64
    WEBMONEY_UNKNOWN = ('payment-method-10',)  # 345, 64

    CARD_RUB = ('payment-method-7', 'payment-method-card_rub')  # 345, 4
    CARD_USD = ('payment-method-card_usd',)  # 345, 4
    CARD_EUR = ('payment-method-card_eur',)  # 345, 4
    CARD_UAH = ('payment-method-card_uah',)  # 345, 4
    CARD_UNKNOWN = ('payment-method-11', 'payment-method-15', 'payment-method-16',
                    'payment-method-25', 'payment-method-26', 'payment-method-27',
                    'payment-method-32', 'payment-method-33', 'payment-method-34', 'payment-method-35',
                    'payment-method-37', 'payment-method-38', 'payment-method-39', 'payment-method-40')  # 345, 4

    MOBILE = ('payment-method-8',)  # 345, 124
    APPLE = ('payment-method-9', 'payment-method-19', 'payment-method-20')  # 345, 154
    MASTERCARD = ('payment-method-12', 'payment-method-22', 'payment-method-23')  # 345, 274
    VISA = ('payment-method-13', 'payment-method-28', 'payment-method-29')  # 345, 304
    GOOGLE = ('payment-method-14', 'payment-method-17', 'payment-method-18')  # 345, 244
    FUNPAY = ('payment-method-24',)  # 345, 214
    LITECOIN = ('payment-method-30',)  # 375, 4
    BINANCE = ('payment-method-31',)  # 375, 34
    BINANCE_USDT = ('payment-method-binance_usdt',)  # 375, 34
    BINANCE_USDC = ('payment-method-binance_usdc',)  # 375, 34
    PAYPAL = ('payment-method-36', 'payment-method-paypal')  # 345, 184
    USDT_TRC = ('payment-method-usdt_trc',)  # 375, 64
    UNKNOWN = ('',)

    # MIR = 26, ('UNKNOWN', ), (345, Y)

    @staticmethod
    @cache
    def css_classes_as_dict() -> MappingProxyType[str, 'PaymentMethod']:
        return MappingProxyType({
            cls: val for val in PaymentMethod for cls in val.value
        })

    @staticmethod
    def get_by_css_class(css_class: str) -> 'PaymentMethod':
        """
        Determine the payment method based on a given CSS class string.

        Examples:
            >>> PaymentMethod.get_by_css_class('some text payment-method-1')
            <PaymentMethod.QIWI: ('payment-method-1', 'payment-method-qiwi')>

            >>> PaymentMethod.get_by_css_class('some_another_css_class')
            <PaymentMethod.UNKNOWN: ('',)>
        """
        classes = PaymentMethod.css_classes_as_dict()
        for cls in classes:
            if classes[cls] is PaymentMethod.UNKNOWN:
                continue

            if cls in css_class:
                return classes[cls]

        return PaymentMethod.UNKNOWN

