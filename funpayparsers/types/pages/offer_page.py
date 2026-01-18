from __future__ import annotations


__all__ = ('OfferPage',)


from typing import TYPE_CHECKING
from dataclasses import dataclass

from funpayparsers.types.pages.base import FunPayPage

if TYPE_CHECKING:
    from funpayparsers.types.common import PaymentOption, DetailedUserBalance
    from funpayparsers.types.chat import Chat
    from funpayparsers.parsers.page_parsers.offer_page_parser import OfferPageParsingOptions


@dataclass
class OfferPage(FunPayPage):
    subcategory_full_name: str
    """Full name of subcategory."""

    auto_delivery: bool
    """Whether auto-delivery is on or off."""

    fields: dict[str, str]
    """Offer fields."""

    chat: Chat
    """Chat with seller."""

    payment_options: dict[str, PaymentOption]
    """Payment options in format {variant_id: PaymentOption}."""

    user_balance: DetailedUserBalance  # user_balance available even on anonymous pages
    """User balance."""

    @classmethod
    def from_raw_source(
        cls, raw_source: str, options: OfferPageParsingOptions | None = None
    ) -> OfferPage:
        from funpayparsers.parsers.page_parsers.offer_page_parser import (
            OfferPageParser,
            OfferPageParsingOptions
        )

        options = options or OfferPageParsingOptions()
        return OfferPageParser(raw_source=raw_source, options=options).parse()
