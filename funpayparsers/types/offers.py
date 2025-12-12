from __future__ import annotations


__all__ = ('OfferPreview', 'OfferSeller', 'OfferFields')

from typing import Any, TypeVar, ParamSpec
from dataclasses import field, dataclass
from collections.abc import Callable

from typing_extensions import Self

from funpayparsers.types.base import FunPayObject
from funpayparsers.types.common import MoneyValue


@dataclass
class OfferSeller(FunPayObject):
    """Represents the seller of an offer."""

    id: int
    """The seller's user ID."""

    username: str
    """The seller's username."""

    online: bool
    """Whether the seller is currently online."""

    avatar_url: str
    """URL of the seller's avatar."""

    registration_date_text: str
    """The seller's registration date (as a formatted string)."""

    rating: int
    """The seller's rating (number of stars)."""

    reviews_amount: int
    """The total number of reviews received by the seller."""

    @property
    def registration_timestamp(self) -> int:
        """
        The seller's registration timestamp.

        ``0``, if an error occurred while parsing.
        """
        from funpayparsers.parsers.utils import parse_date_string

        try:
            return parse_date_string(self.registration_date_text)
        except ValueError:
            return 0


@dataclass
class OfferPreview(FunPayObject):
    """Represents an offer preview."""

    id: int | str
    """Unique offer ID."""

    auto_delivery: bool
    """Whether auto delivery is enabled for this offer."""

    is_pinned: bool
    """Whether this offer is pinned to the top of the list."""

    title: str | None
    """Offer title, if exists."""

    amount: int | None
    """The quantity of goods available in this offer, if specified."""

    price: MoneyValue
    """The price of the offer."""

    seller: OfferSeller | None
    """Information about the offer seller, if applicable."""

    other_data: dict[str, str | int]
    """
    Additional data related to the offer, such as server ID, side ID, etc., 
    if applicable.
    """

    other_data_names: dict[str, str]
    """
    Human-readable names corresponding to entries in ``other_data``, if applicable.
    
    Not all entries, that are exists in ``OfferPreview.other_data`` can be found here
    (not all entries have a name).
    """

    disabled: bool = False
    """Whether the offer is disabled (alias, defaults to ``False``)."""


T = TypeVar('T')
P = ParamSpec('P')


def chips_only(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        obj: OfferFields = args[0]  # type: ignore
        if not obj.is_currency:
            raise RuntimeError(
                f'Instance of {obj.__class__.__name__} is not describing a chips lot fields.\n'
                f'Use {obj.__class__.__name__}.convert_to_chip to convert it to chips lot fields.'
            )
        return func(*args, **kwargs)

    return wrapper


def common_only(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        obj: OfferFields = args[0]  # type: ignore
        if not obj.is_common:
            raise RuntimeError(
                f'Instance of {obj.__class__.__name__} is not describing a common lot fields.\n'
                f'Use {obj.__class__.__name__}.convert_to_common to convert it to common lot fields.'
            )
        return func(*args, **kwargs)

    return wrapper


@dataclass
class OfferFields(FunPayObject):
    """
    Represents the full set of form fields used to construct or update
    an offer on FunPay.

    This class acts as a wrapper around a dictionary of raw form field values
    and provides properties for commonly used fields.

    It is **strongly recommended** to modify offer fields via
    class properties (e.g. ``title_ru``, ``active``, ``images``),
    as they handle proper value formatting and conversions expected by FunPay.

    If no property exists for a particular field,
    use ``set_field(key, value)`` to set it manually,
    making sure to pass a value already formatted for FunPay.

    Setting a field to ``None`` via a property or ``set_field()``
    will automatically remove the corresponding key from ``fields_dict``.

    Examples:
        >>> fields = OfferFields(raw_source='{}', fields_dict={})
        >>> fields.title_ru = "My Offer Name"
        >>> fields.fields_dict
        {'fields[summary][ru]': 'My Offer Name'}
        >>> fields.title_ru = None
        >>> fields.fields_dict
        {}
        >>> fields.active = True
        >>> fields.fields_dict
        {'active': 'on'}
    """

    fields_dict: dict[str, str] = field(default_factory=dict)
    """All fields as dict."""

    def __post_init__(self) -> None:
        if 'csrf_token' in self.fields_dict:
            del self.fields_dict['csrf_token']

    def set_field(self, key: str, value: Any) -> None:
        """
        Manually set or remove a raw field value.

        :param key: The raw field name (e.g. ``"fields[summary][ru]"``).
        :param value: The value to set. If
            ``None``, the field is removed from `fields_dict`.

        .. note:
            Only use this method if a dedicated property for the field does not exist.
            Ensure the ``value`` is formatted exactly as expected by FunPay.
        """
        if value is None:
            self.fields_dict.pop(key, None)
        else:
            if not isinstance(value, str):
                value = str(value)
            self.fields_dict[key] = value

    def convert_to_currency(self, category_id: int, subcategory_id: int) -> Self:
        """
        Transform this `OfferFields` instance into a **currency offer** configuration.

        This operation:
            1. **Clears** all existing fields in ``fields_dict``.
            2. Sets the ``category_id`` (``game`` field).
            3. Sets the ``subcategory_id`` (``chip`` field).

        After calling this method, the instance will be considered a *currency-type* offer
        (``is_currency`` will return ``True``), meaning currency-specific setters/getters (like
        ``set_currency_amount``) become applicable and common-specific setters/getters
        will no longer apply.

        :param category_id: Category ID.
        :param subcategory_id: Subcategory ID.

        :return: The modified instance (self).
        """
        self.fields_dict.clear()
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        return self

    def convert_to_common(self, subcategory_id: int | None, offer_id: int) -> Self:
        """
        Transform this `OfferFields` instance into a **common offer** configuration.

        This operation:
            1. **Clears** all existing fields in ``fields_dict``.
            2. Sets the ``subcategory_id`` (``node_id`` field).
            3. Sets the ``offer_id`` (``offer_id`` field).

        After calling this method, the instance will be considered a *common-type* offer
        (``is_currency`` will return ``False``), meaning common-specific setters/getters (like
        ``offer_id``) become applicable and currency-specific setters/getters
        will no longer apply.

        :param subcategory_id: Subcategory ID.
        :param offer_id: Offer ID.

        :return: The modified instance (self).
        """
        self.fields_dict.clear()
        self.subcategory_id = subcategory_id
        self.offer_id = offer_id
        return self

    def get_currency_amount(self, server_id: int, side_id: int) -> float | None:
        """
        Gets the currency amount.

        Applicable for currency offers only.

        Field name: ``offer[<server_id>][<side_id>][amount]``

        :param server_id: Server ID.
        :param side_id: Side ID.
        """
        if not self.fields_dict.get(f'offer[{server_id}][{side_id}][amount]'):
            return None
        return float(self.fields_dict[f'offer[{server_id}][{side_id}][amount]'])

    @chips_only
    def set_currency_amount(
        self, server_id: int, side_id: int, amount: int | float | None
    ) -> None:
        """
        Sets the currency amount.

        Applicable for currency offers only.

        Field name: ``offer[<server_id>][<side_id>][amount]``

        :param server_id: Server ID.
        :param side_id: Side ID.
        :param amount: Currency amount.
        """
        self.set_field(f'offer[{server_id}][{side_id}][amount]', amount)

    def get_currency_price(self, server_id: int, side_id: int) -> float | None:
        """
        Gets the currency price.

        Applicable for currency offers only.

        Field name: ``offer[<server_id>][<side_id>][price]``

        :param server_id: Server ID.
        :param side_id: Side ID.
        """
        if not self.fields_dict.get(f'offer[{server_id}][{side_id}][price]'):
            return None
        return float(self.fields_dict[f'offer[{server_id}][{side_id}][price]'])

    @chips_only
    def set_currency_price(self, server_id: int, side_id: int, price: int | float | None) -> None:
        """
        Sets the currency price.

        Applicable for currency offers only.

        Field name: ``offer[<server_id>][<side_id>][price]``

        :param server_id: Server ID.
        :param side_id: Side ID.
        :param price: Currency price.
        """
        self.set_field(f'offer[{server_id}][{side_id}][price]', price)

    def get_currency_status(self, server_id: int, side_id: int) -> bool | None:
        """
        Gets the currency active status.

        Applicable for currency offers only.

        Field name: ``offer[<server_id>][<side_id>][active]``

        :param server_id: Server ID.
        :param side_id: Side ID.
        """
        return self.fields_dict.get(f'offer[{server_id}][{side_id}][active]') == 'on'

    @chips_only
    def set_currency_status(self, server_id: int, side_id: int, status: bool | None) -> None:
        """
        Sets the currency active status.

        Applicable for currency offers only.

        Field name: ``offer[<server_id>][<side_id>][active]``

        :param server_id: Server ID.
        :param side_id: Side ID.
        :param status: Active status.
        """
        self.set_field(
            f'offer[{server_id}][{side_id}][active]',
            'on' if status else '' if status is not None else None,
        )

    @property
    def is_currency(self) -> bool:
        """
        Whether this ``OfferFields`` instance is a currency-type or not.
        """
        return 'game' in self.fields_dict

    @property
    def is_common(self) -> bool:
        """
        Whether this ``OfferFields`` instance is a common-type or not.
        """
        return 'game' not in self.fields_dict

    @property
    def subcategory_id(self) -> int | None:
        """
        Subcategory ID.

        Field name: ``node_id`` for common offers, ``chip`` for currency offers.
        """
        if self.is_currency:
            result = self.fields_dict.get('chip')
        else:
            result = self.fields_dict.get('node_id')
        if not result:
            return None
        return int(result)

    @subcategory_id.setter
    def subcategory_id(self, value: int | None) -> None:
        if self.is_currency:
            self.set_field('chip', value)
        else:
            self.set_field('node_id', value)

    @property
    def category_id(self) -> int | None:
        """
        Category ID.

        Applicable for common offers only.

        Field name: ``game``.
        """
        if not self.fields_dict.get('game'):
            return None
        return int(self.fields_dict['game'])

    @category_id.setter
    @chips_only
    def category_id(self, value: int | None) -> None:
        self.set_field('game', value)

    @property
    def min_sum(self) -> float | None:
        """
        Minimum order sum.

        Applicable for currency offers only.

        Field name: ``chip_min_sum``.
        """
        if not self.fields_dict.get('chip_min_sum'):
            return None
        return float(self.fields_dict['chip_min_sum'])

    @min_sum.setter
    @chips_only
    def min_sum(self, value: float | int | None) -> None:
        """
        Offer title (Russian).

        Applicable for common offers only.

        Field name: ``fields[summary][ru]``
        """
        self.set_field('chip_min_sum', value)

    @property
    def offer_id(self) -> int | None:
        """
        Offer ID.
        Set to 0 and provide ``subcategory_id`` if you want to create a new offer.

        Applicable for common offers only.

        Field name: ``offer_id``
        """
        if not self.fields_dict.get('offer_id'):
            return None
        return int(self.fields_dict['offer_id'])

    @offer_id.setter
    @common_only
    def offer_id(self, offer_id: int | None) -> None:
        self.set_field('offer_id', offer_id)

    @property
    def title_ru(self) -> str | None:
        """
        Offer title (Russian).

        Applicable for common offers only.

        Field name: ``fields[summary][ru]``
        """
        return self.fields_dict.get('fields[summary][ru]')

    @title_ru.setter
    @common_only
    def title_ru(self, value: str | None) -> None:
        self.set_field('fields[summary][ru]', value)

    @property
    def title_en(self) -> str | None:
        """
        Offer title (English).

        Applicable for common offers only.

        Field name: ``fields[summary][en]``
        """
        return self.fields_dict.get('fields[summary][en]')

    @title_en.setter
    @common_only
    def title_en(self, value: str | None) -> None:
        self.set_field('fields[summary][en]', value)

    @property
    def desc_ru(self) -> str | None:
        """
        Offer description (Russian).

        Applicable for common offers only.

        Field name: ``fields[desc][ru]``
        """
        return self.fields_dict.get('fields[desc][ru]')

    @desc_ru.setter
    @common_only
    def desc_ru(self, value: str | None) -> None:
        self.set_field('fields[desc][ru]', value)

    @property
    def desc_en(self) -> str | None:
        """
        Offer description (English).

        Applicable for common offers only.

        Field name: ``fields[desc][en]``
        """
        return self.fields_dict.get('fields[desc][en]')

    @desc_en.setter
    @common_only
    def desc_en(self, value: str | None) -> None:
        self.set_field('fields[desc][en]', value)

    @property
    def payment_msg_ru(self) -> str | None:
        """
        Payment message (Russian).

        Applicable for common offers only.

        Field name: ``fields[payment_msg][ru]``
        """
        return self.fields_dict.get('fields[payment_msg][ru]')

    @payment_msg_ru.setter
    @common_only
    def payment_msg_ru(self, value: str | None) -> None:
        self.set_field('fields[payment_msg][ru]', value)

    @property
    def payment_msg_en(self) -> str | None:
        """
        Payment message (English).

        Applicable for common offers only.

        Field name: ``fields[payment_msg][en]``
        """
        return self.fields_dict.get('fields[payment_msg][en]')

    @payment_msg_en.setter
    @common_only
    def payment_msg_en(self, value: str | None) -> None:
        self.set_field('fields[payment_msg][en]', value)

    @property
    def images(self) -> list[int] | None:
        """
        List of image IDs.

        Applicable for common offers only.

        Field name: ``fields[images]``
        """
        images = self.fields_dict.get('fields[images]')
        if images is None:
            return None
        return [int(i) for i in images.split(',')]

    @images.setter
    @common_only
    def images(self, value: list[int] | None) -> None:
        self.set_field(
            'fields[images]',
            ','.join(str(i) for i in value) if value is not None else None,
        )

    @property
    def secrets(self) -> list[str] | None:
        """
        List of goods in auto delivery.

        Applicable for common offers only.

        Field name: ``fields[secrets]``
        """
        goods = self.fields_dict.get('fields[secrets]')
        if goods is None:
            return None
        return goods.split('\n')

    @secrets.setter
    @common_only
    def secrets(self, value: list[str] | None) -> None:
        self.set_field('fields[secrets]', '\n'.join(value) if value is not None else None)

    @property
    def active(self) -> bool:
        """
        Whether the offer is active or not.

        Applicable for common offers only.

        Field name: ``fields[active]``
        """
        return self.fields_dict.get('active') == 'on'

    @active.setter
    @common_only
    def active(self, value: bool | None) -> None:
        self.set_field('active', 'on' if value else '' if value is not None else None)

    @property
    def auto_delivery(self) -> bool:
        """
        Whether the auto_delivery is enabled for this offer or not.

        Applicable for common offers only.

        Field name: ``fields[auto_delivery]``
        """
        return self.fields_dict.get('auto_delivery') == 'on'

    @auto_delivery.setter
    @common_only
    def auto_delivery(self, value: bool | None) -> None:
        self.set_field('auto_delivery', 'on' if value else '' if value is not None else None)

    @property
    def deactivate_after_sale(self) -> bool:
        """
        Whether the deactivation after sale is enabled for this offer or not.

        Applicable for common offers only.

        Field name: ``fields[deactivate_after_sale]``
        """
        return self.fields_dict.get('deactivate_after_sale') == 'on'

    @deactivate_after_sale.setter
    @common_only
    def deactivate_after_sale(self, value: bool | None) -> None:
        self.set_field(
            'deactivate_after_sale',
            'on' if value else '' if value is not None else None,
        )

    @property
    def price(self) -> float | None:
        """
        Offer price.

        Applicable for common offers only.

        Field name: ``price``
        """
        if not self.fields_dict.get('price'):
            return None
        return float(self.fields_dict['price'])

    @price.setter
    @common_only
    def price(self, value: float) -> None:
        self.set_field('price', str(value))

    @property
    def amount(self) -> int | None:
        """
        Goods amount.

        Applicable for common offers only.

        Field name: ``amount``
        """
        if not self.fields_dict.get('amount'):
            return None
        return int(self.fields_dict['amount'])

    @amount.setter
    @common_only
    def amount(self, value: int | None) -> None:
        self.set_field('amount', value)
