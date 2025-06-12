__all__ = ('OrderStatus', 'Currency', 'TransactionStatus', 'PaymentMethod')


from enum import StrEnum, Enum, verify, UNIQUE


@verify(UNIQUE)
class OrderStatus(StrEnum):
    """
    Order statuses enumeration.

    Each value is a css class, that identifies order status.
    """

    PAID = 'text-primary'
    """Paid, but not complete order."""

    COMPLETE = 'text-success'
    """Completed order."""

    REFUNDED = 'text-warning'
    """Refunded order."""

    UNKNOWN = 'unknown'
    """Unknown status. Just in case, for future FunPay updates."""


    @staticmethod
    def get_by_css_class(css_class: str) -> 'OrderStatus':
        """
        Determines the order status based on a given CSS class string.

        >>> OrderStatus.get_by_css_class('text-primary some_another_css_class')
        <OrderStatus.PAID: 'text-primary'>

        >>> OrderStatus.get_by_css_class('some_another_css_class text-warning')
        <OrderStatus.REFUNDED: 'text-warning'>

        >>> OrderStatus.get_by_css_class('some_another_css_class text-success')
        <OrderStatus.COMPLETE: 'text-success'>

        >>> OrderStatus.get_by_css_class('some_another_css_class')
        <OrderStatus.UNKNOWN: 'unknown'>
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

    UNK = ''
    """Unknown currency. Just in case, for future FunPay updates."""

    RUB = '₽'
    USD = '$'
    EUR = '€'
    UAH = '.'  # todo: does funpay has UAH currency?

    @staticmethod
    def get_by_character(character: str) -> 'Currency':
        """
        Determines the currency based on a given currency string.

        >>> Currency.get_by_character('$')
        <Currency.USD: '$'>

        >>> Currency.get_by_character('₽')
        <Currency.RUB: '₽'>

        >>> Currency.get_by_character('€')
        <Currency.EUR: '€'>
        """
        for i in Currency:
            if i is Currency.UNK:
                continue
            if character == i.value:
                return i
        return Currency.UNK


@verify(UNIQUE)
class TransactionStatus(Enum):
    ...


@verify(UNIQUE)
class PaymentMethod(Enum):
    ...
