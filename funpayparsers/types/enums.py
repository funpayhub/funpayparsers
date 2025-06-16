__all__ = (
    'Currency',
    'OrderStatus',
    'PaymentMethod',
    'SubcategoryType',
    'TransactionStatus',
    'BadgeType',
)


from enum import UNIQUE, Enum, StrEnum, verify


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
class PaymentMethod(Enum): ...


@verify(UNIQUE)
class SystemMessageType(Enum): ...


@verify(UNIQUE)
class BadgeType(StrEnum):
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
