from __future__ import annotations


__all__ = ('OfferPreview', 'OfferSeller', 'OfferFields')

from dataclasses import field, dataclass

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

    register_date_text: str
    """The seller's registration date (as a formatted string)."""

    rating: int
    """The seller's rating (number of stars)."""

    reviews_amount: int
    """The total number of reviews received by the seller."""


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

    def set_field(self, key: str, value: str | None) -> None:
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
            self.fields_dict[key] = str(value)

    @property
    def csrf_token(self) -> str | None:
        """
        CSRF token of the current user.

        Field name: ``csrf_token``
        """
        return self.fields_dict.get('csrf_token')

    @csrf_token.setter
    def csrf_token(self, value: str | None) -> None:
        self.set_field('csrf_token', value)

    @property
    def title_ru(self) -> str | None:
        """
        Offer title (Russian).

        Field name: ``fields[summary][ru]``
        """
        return self.fields_dict.get('fields[summary][ru]')

    @title_ru.setter
    def title_ru(self, value: str | None) -> None:
        self.set_field('fields[summary][ru]', value)

    @property
    def title_en(self) -> str | None:
        """
        Offer title (English).

        Field name: ``fields[summary][en]``
        """
        return self.fields_dict.get('fields[summary][en]')

    @title_en.setter
    def title_en(self, value: str | None) -> None:
        self.set_field('fields[summary][en]', value)

    @property
    def desc_ru(self) -> str | None:
        """
        Offer description (Russian).

        Field name: ``fields[desc][ru]``
        """
        return self.fields_dict.get('fields[desc][ru]')

    @desc_ru.setter
    def desc_ru(self, value: str | None) -> None:
        self.set_field('fields[desc][ru]', value)

    @property
    def desc_en(self) -> str | None:
        """
        Offer description (English).

        Field name: ``fields[desc][en]``
        """
        return self.fields_dict.get('fields[desc][en]')

    @desc_en.setter
    def desc_en(self, value: str | None) -> None:
        self.set_field('fields[desc][en]', value)

    @property
    def payment_msg_ru(self) -> str | None:
        """
        Payment message (Russian).

        Field name: ``fields[payment_msg][ru]``
        """
        return self.fields_dict.get('fields[payment_msg][ru]')

    @payment_msg_ru.setter
    def payment_msg_ru(self, value: str | None) -> None:
        self.set_field('fields[payment_msg][ru]', value)

    @property
    def payment_msg_en(self) -> str | None:
        """
        Payment message (English).

        Field name: ``fields[payment_msg][en]``
        """
        return self.fields_dict.get('fields[payment_msg][en]')

    @payment_msg_en.setter
    def payment_msg_en(self, value: str | None) -> None:
        self.set_field('fields[payment_msg][en]', value)

    @property
    def images(self) -> list[int] | None:
        """
        List of image IDs.

        Field name: ``fields[images]``
        """
        images = self.fields_dict.get('fields[images]')
        if images is None:
            return None
        return [int(i) for i in images.split(',')]

    @images.setter
    def images(self, value: list[int] | None) -> None:
        self.set_field(
            'fields[images]',
            ','.join(str(i) for i in value) if value is not None else None,
        )

    @property
    def secrets(self) -> list[str] | None:
        """
        List of goods in auto delivery.

        Field name: ``fields[secrets]``
        """
        goods = self.fields_dict.get('fields[secrets]')
        if goods is None:
            return None
        return goods.split('\n')

    @secrets.setter
    def secrets(self, value: list[str] | None) -> None:
        self.set_field('fields[secrets]', '\n'.join(value) if value is not None else None)

    @property
    def active(self) -> bool:
        """
        Whether the offer is active or not.

        Field name: ``fields[active]``
        """
        return self.fields_dict.get('active') == 'on'

    @active.setter
    def active(self, value: bool | None) -> None:
        self.set_field('active', 'on' if value else '' if value is not None else None)

    @property
    def auto_delivery(self) -> bool:
        """
        Whether the auto_delivery is enabled for this offer or not.

        Field name: ``fields[auto_delivery]``
        """
        return self.fields_dict.get('auto_delivery') == 'on'

    @auto_delivery.setter
    def auto_delivery(self, value: bool | None) -> None:
        self.set_field('auto_delivery', 'on' if value else '' if value is not None else None)

    @property
    def deactivate_after_sale(self) -> bool:
        """
        Whether the deactivation after sale is enabled for this offer or not.

        Field name: ``fields[deactivate_after_sale]``
        """
        return self.fields_dict.get('deactivate_after_sale') == 'on'

    @deactivate_after_sale.setter
    def deactivate_after_sale(self, value: bool | None) -> None:
        self.set_field(
            'deactivate_after_sale',
            'on' if value else '' if value is not None else None,
        )
