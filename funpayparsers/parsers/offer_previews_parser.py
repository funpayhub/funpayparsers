from __future__ import annotations


__all__ = ('OfferPreviewsParser', 'OfferPreviewsParsingOptions')

import re
from dataclasses import dataclass
from copy import deepcopy

from selectolax.lexbor import LexborNode

from funpayparsers.types.enums import SubcategoryType, SubcategoryFieldType
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.offers import OfferSeller, OfferPreview
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)
from funpayparsers.types.subcategory_structure import SubcategoryStructure


@dataclass(frozen=True)
class OfferPreviewsParsingOptions(ParsingOptions):
    """Options class for ``OfferPreviewsParser``."""

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``OfferPreviewsParser``.

    ``parsing_mode`` and ``parse_value_from_attribute`` options are hardcoded in
    ``OfferPreviewsParser`` and is therefore ignored if provided externally.

    Defaults to ``UserPreviewParsingOptions()``.
    """

    subcategory_structure: SubcategoryStructure | None = None
    """
    Optional subcategory field structure.

    When provided:

    - **Catalog pages** (``data-f-*`` attributes present): ``other_data_names`` is
      enriched with FunPay labels from the structure (e.g.
      ``{'arena': 'Арена', 'level': 'Уровень'}``).
    - **Profile / sells pages** (title-only, no ``data-f-*``): field values are
      extracted from the comma-separated title suffix and stored in ``other_data``
      and ``other_data_names`` (best-effort; conditional fields are treated as always
      visible, which may cause misalignment for subcategories with competing
      conditions).

    Defaults to ``None``.
    """

    subcategory_id: int | None = None
    """Subcategory ID to stamp on every parsed ``OfferPreview``. Defaults to ``None``."""

    subcategory_type: SubcategoryType | None = None
    """Subcategory type to stamp on every parsed ``OfferPreview``. Defaults to ``None``."""

    category_text: str | None = None
    """
    Raw category label to stamp on every parsed ``OfferPreview``.
    Use when only a text description of the category is available.
    Defaults to ``None``.
    """



class OfferPreviewsParser(
    FunPayHTMLObjectParser[list[OfferPreview], OfferPreviewsParsingOptions],
):
    """
    Class for parsing public offer previews.

    Possible locations:
        - User profile pages (https://funpay.com/<userid>/).
        - On subcategories offer list pages
        (https://funpay.com/<lots/chips>/<subcategory_id>).
    """

    def _parse(self) -> list[OfferPreview]:
        result = []

        # don't add these data-fields to OfferPreview.other_data,
        # cz there are specific fields in OfferPreview class for them.
        skip_data = ['data-online', 'data-auto']

        # don't look for these human-readable names for this data-fields,
        # cz there are specific fields in OfferPreview class for them.
        skip_match_data = ['user', 'online', 'auto']

        processed_users: dict[str, OfferSeller] = {}

        for offer_div in self.tree.css('a.tc-item'):
            url: str = offer_div.attributes['href']  # type: ignore[assignment] # always has href

            if data_offer := offer_div.attributes.get('data-offer', None):
                offer_id_str = data_offer
            else:
                offer_id_str = url.split('id=')[1]

            desc_divs = offer_div.css('div.tc-desc-text')
            # currency offers don't have description.
            desc = desc_divs[0].text(strip=True) if desc_divs else None

            # Currency offers have 'data-s' attribute in tc-amount div,
            # where amount is stored.
            #
            # Common offers don't have it, so we need to parse tc-amount divs text.
            #
            # Common offers don't have tc-amount div, if the seller didn't
            # specify the amount of goods.
            amount_div = offer_div.css('div.tc-amount')
            if amount_div:
                amount_str = amount_div[0].attributes.get('data-s') or amount_div[0].text(
                    strip=True
                )
                amount = int(amount_str) if amount_str.isnumeric() else None
                unit_div = amount_div[0].css_first('span', strict=False)
                if unit_div:
                    unit = unit_div.text(strip=True)
                else:
                    unit = None
            else:
                amount = None
                unit = None

            price_div = offer_div.css('div.tc-price')[0]
            price = MoneyValueParser(
                price_div.html or '',
                options=self.options.money_value_parsing_options,
                parsing_mode=MoneyValueParsingMode.FROM_OFFER_PREVIEW,
                parse_value_from_attribute=(
                    False if 'chips' in offer_div.attributes['href'] else True  # type: ignore[operator]
                ),
            ).parse()

            seller = self._parse_user_tag(offer_div, processed_users)

            struct = self.options.subcategory_structure

            additional_data: dict[str, str | int] = {}
            names: dict[str, str] = {}

            if struct is not None:
                for key, data in offer_div.attributes.items():
                    if not key.startswith('data-') or key in skip_data:
                        continue
                    if data is None:
                        continue
                    # Strip data-f- prefix for subcategory field keys, data- for others.
                    normalized_key = (
                        key[len('data-f-'):] if key.startswith('data-f-') else key[len('data-'):]
                    )
                    additional_data[normalized_key] = int(data) if data.isnumeric() else data

                for data_key in additional_data:
                    if data_key in skip_match_data:
                        continue
                    divs = offer_div.css(f'div.tc-{data_key}')
                    if not divs:
                        continue
                    names[data_key] = divs[0].text(strip=True)

            if struct is not None:
                has_field_data = any(k in struct.field_map for k in additional_data)
                if has_field_data:
                    # Case A: catalog page — data-f-* keys map to known field IDs.
                    for k in additional_data:
                        if k in struct.field_map:
                            names[k] = struct.field_map[k].label
                elif desc is not None:
                    # Case B: profile/sells page — extract field values from title.
                    title_data, title_names = self._extract_title_fields(desc, struct)
                    additional_data.update(title_data)
                    names.update(title_names)

            result.append(
                OfferPreview(
                    raw_source=offer_div.html or '',
                    id=int(offer_id_str) if offer_id_str.isnumeric() else offer_id_str,
                    auto_delivery=bool(offer_div.attributes.get('data-auto')),
                    is_pinned=bool(offer_div.attributes.get('data-user')),
                    title=desc,
                    amount=amount,
                    unit=unit,
                    price=price,
                    seller=seller,
                    other_data=additional_data,
                    other_data_names=names,
                    disabled='warning' in (offer_div.attributes.get('class') or ''),
                    subcategory_id=self.options.subcategory_id,
                    subcategory_type=self.options.subcategory_type,
                    category_text=self.options.category_text,
                )
            )

        return result

    @staticmethod
    def _extract_title_fields(
        title: str, struct: SubcategoryStructure
    ) -> tuple[dict[str, str | int], dict[str, str]]:
        """
        Extract field values from a comma-separated offer title suffix.

        FunPay builds offer titles as ``<summary>, <field1>, <field2>, ...`` where
        each ``<fieldN>`` is the display value for a ``NUMERIC_RANGE``, ``SELECT``,
        or ``DROPDOWN`` field, in declaration order.

        For ``NUMERIC_RANGE`` fields the numeric portion is extracted (e.g.
        ``'15 арена'`` → ``15``).  For select fields the raw string is kept.

        This is best-effort: conditional fields are treated as always visible,
        so subcategories with competing conditions may produce misaligned results.
        """
        suffix_types = {
            SubcategoryFieldType.NUMERIC_RANGE,
            SubcategoryFieldType.SELECT,
            SubcategoryFieldType.DROPDOWN,
        }
        suffix_fields = [f for f in struct.fields if f.type in suffix_types]
        if not suffix_fields:
            return {}, {}

        parts = title.rsplit(', ', maxsplit=len(suffix_fields))
        field_values = parts[1:]  # parts[0] = summary text (may contain commas itself)

        other_data: dict[str, str | int] = {}
        for field_def, raw_val in zip(suffix_fields, field_values):
            if field_def.type == SubcategoryFieldType.NUMERIC_RANGE:
                m = re.match(r'^(\d+(?:\.\d+)?)', raw_val.strip())
                other_data[field_def.id] = int(float(m.group(1))) if m else raw_val
            else:
                other_data[field_def.id] = raw_val

        other_data_names: dict[str, str] = {
            fd.id: fd.label for fd in suffix_fields if fd.id in other_data
        }
        return other_data, other_data_names

    @staticmethod
    def _parse_user_tag(
        offer_tag: LexborNode, processed_users: dict[str, OfferSeller]
    ) -> OfferSeller | None:
        # If this offer preview is from sellers page,
        # and not from subcategory offers page, there is no user div.
        user_divs = offer_tag.css('div.tc-user')
        if not user_divs:
            return None

        user_div = user_divs[0]
        username = user_div.css('div.media-user-name')[0].text(strip=True)
        if username in processed_users:
            return deepcopy(processed_users[username])

        avatar_tag = user_div.css_first('div.avatar-photo')
        user_id = int(avatar_tag.attributes['data-href'].split('/')[-2])  # type: ignore[union-attr]
        # always has data-href
        avatar_tag_style: str = avatar_tag.attributes['style']  # type: ignore[assignment]  # always has style

        # If the user has fewer than 10 reviews or registered less than a month ago,
        # the rating stars are not shown. The number of reviews is displayed
        # as "N reviews" (or "No reviews" if there are none).
        # Otherwise, the user sees rating stars along with the number
        # of reviews next to them.
        stars_amount = len(user_div.css('i.fas'))
        if stars_amount:
            reviews_amount = int(
                user_div.css('span.rating-mini-count')[0].text(deep=True, strip=True)
            )
        else:
            reviews_amount_txt = user_div.css('div.media-user-reviews')[0].text(
                deep=True, strip=True
            )
            reviews_amount_find = re.findall(r'\d+', reviews_amount_txt)
            reviews_amount = int(reviews_amount_find[0]) if reviews_amount_find else 0

        result = OfferSeller(
            raw_source=user_div.html or '',
            id=user_id,
            username=username,
            online=bool(offer_tag.attributes.get('data-online')),
            avatar_url=extract_css_url(avatar_tag_style),
            registration_date_text=(
                user_div.css('div.media-user-info')[0].text(deep=True, strip=True)
            ),
            rating=stars_amount,
            reviews_amount=reviews_amount,
        )

        processed_users[username] = result
        return result
