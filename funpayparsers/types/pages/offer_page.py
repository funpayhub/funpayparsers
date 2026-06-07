from __future__ import annotations


__all__ = ('OfferPage',)


from typing import TYPE_CHECKING
from dataclasses import field, dataclass

from funpayparsers.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpayparsers.types.chat import Chat
    from funpayparsers.types.common import PaymentOption, DetailedUserBalance
    from funpayparsers.parsers.page_parsers.offer_page_parser import OfferPageParsingOptions
    from funpayparsers.types.subcategory_structure import SubcategoryStructure


@dataclass
class OfferPage(FunPayPage):
    subcategory_full_name: str
    """Full name of subcategory."""

    auto_delivery: bool
    """Whether auto-delivery is on or off."""

    fields: dict[str, str]
    """
    Offer fields from ``div.param-list``.

    Keys are human-readable FunPay labels (e.g. ``'Арена'``),
    values are display strings (e.g. ``'15'``).
    """

    chat: Chat
    """Chat with seller."""

    payment_options: dict[str, PaymentOption]
    """Payment options in format {variant_id: PaymentOption}."""

    user_balance: DetailedUserBalance  # user_balance available even on anonymous pages
    """User balance."""

    images: list[str] = field(default_factory=list)
    """Full-size image URLs extracted from attachment items in ``div.param-list``."""

    def get_structured_fields(self, structure: SubcategoryStructure) -> dict[str, str]:
        """Return ``fields`` remapped to FunPay field IDs using *structure*'s label map."""
        return {
            structure.lower_label_map[label.lower()]: val
            for label, val in self.fields.items()
            if label.lower() in structure.lower_label_map
        }

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: OfferPageParsingOptions | None = None
    ) -> OfferPage:
        from funpayparsers.parsers.page_parsers.offer_page_parser import (
            OfferPageParser,
            OfferPageParsingOptions,
        )

        options = options or OfferPageParsingOptions()
        return OfferPageParser(raw_source=raw_source, options=options).parse()
