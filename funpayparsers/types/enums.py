__all__ = ('OrderStatus', 'Currency', 'TransactionStatus', 'PaymentMethod')


from enum import StrEnum, Enum, verify, UNIQUE


@verify(UNIQUE)
class OrderStatus(StrEnum):
    PAID = 'text-primary'
    COMPLETE = 'text-success'
    REFUNDED = 'text-warning'
    UNKNOWN = 'unknown'



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
class Currency(Enum):
    UNK = 0
    RUB = 1
    USD = 2
    EUR = 3
    UAH = 4


@verify(UNIQUE)
class TransactionStatus(Enum):
    ...


@verify(UNIQUE)
class PaymentMethod(Enum):
    ...
