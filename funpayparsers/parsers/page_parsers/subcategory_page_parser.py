from __future__ import annotations


__all__ = ('SubcategoryPageParsingOptions', 'SubcategoryPageParser')

from dataclasses import dataclass

from funpayparsers.types.enums import SubcategoryType, SubcategoryFieldType
from funpayparsers.types.pages import SubcategoryPage
from funpayparsers.types.offers import OfferPreview
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.categories import Subcategory
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)
from funpayparsers.parsers.offer_previews_parser import (
    OfferPreviewsParser,
    OfferPreviewsParsingOptions,
)
from funpayparsers.parsers.offer_fields_parser import OfferFieldsParser
from funpayparsers.types.subcategory_structure import (
    SubcategoryFieldDef,
    SubcategoryStructure,
)


def _synthesize_chips_structure(
    subcategory_id: int, offers: list[OfferPreview]
) -> SubcategoryStructure:
    """
    Build a synthetic ``SubcategoryStructure`` from CHIPS offer previews.

    Used when a CHIPS subcategory listing has no ``div.lot-fields`` block, so
    no authoritative structure can be parsed. Each distinct key seen across
    ``OfferPreview.other_data`` becomes a ``SubcategoryFieldDef`` of type
    ``SELECT`` whose ``options`` are the union of values for that key, in
    first-seen order. Labels come from ``OfferPreview.other_data_names`` if
    present, otherwise fall back to the field id.

    The resulting structure is marked ``derived_from='chips_offers'`` so
    callers can distinguish it from authoritative ones.
    """
    field_options: dict[str, list[str]] = {}
    field_labels: dict[str, str] = {}

    for offer in offers:
        if offer.other_data:
            for fid, val in offer.other_data.items():
                sval = str(val)
                opts = field_options.setdefault(fid, [])
                if sval not in opts:
                    opts.append(sval)
        if offer.other_data_names:
            for fid, name in offer.other_data_names.items():
                if fid not in field_labels and name:
                    field_labels[fid] = name

    fields = {
        fid: SubcategoryFieldDef(
            raw_source='',
            id=fid,
            type=SubcategoryFieldType.SELECT,
            label=field_labels.get(fid, fid),
            conditions=[],
            options=opts,
            aliases=set(),
        )
        for fid, opts in field_options.items()
    }

    return SubcategoryStructure(
        raw_source='',
        subcategory_id=subcategory_id,
        fields=fields,
        derived_from='chips_offers',
    )


@dataclass(frozen=True)
class SubcategoryPageParsingOptions(ParsingOptions):
    """Options class for ``SubcategoryPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, 
    which is used by ``SubcategoryPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``SubcategoryPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    offer_previews_parsing_options: OfferPreviewsParsingOptions = OfferPreviewsParsingOptions()
    """
    Options instance for ``OfferPreviewsParser``,
    which is used by ``SubcategoryPageParser``.

    Defaults to ``OfferPreviewsParsingOptions()``.
    """

    fallback_structure_from_chips_offers: bool = False
    """
    For CHIPS subcategories whose listing page has no ``div.lot-fields``:
    synthesize a ``SubcategoryStructure`` from the union of
    ``OfferPreview.other_data`` keys/values across the parsed offers (see
    :func:`_synthesize_chips_structure`).

    Each distinct key becomes a ``SubcategoryFieldDef`` of type ``SELECT``
    whose ``options`` are the values seen across offers, in first-seen order.
    The result is marked ``derived_from='chips_offers'`` so callers can
    distinguish synthetic structures from authoritative ones.

    Default ``False`` for backwards compatibility — opt-in.
    """


class SubcategoryPageParser(
    FunPayHTMLObjectParser[
        SubcategoryPage,
        SubcategoryPageParsingOptions,
    ]
):
    """
    Class for parsing subcategory offer list pages
    (`https://funpay.com/<lots/chips>/<subcategory_id>/`).
    """

    def _parse(self) -> SubcategoryPage:
        showcase = self.tree.css_first('div.showcase')

        # lot-ID / chips-ID
        subcategory_id_str: str = showcase.attributes['data-section']  # type: ignore[assignment]
        # always has 'data-section'
        related_subcategories = []
        subcategory_type = SubcategoryType.from_showcase_data_section(subcategory_id_str)

        for i in self.tree.css('a.counter-item'):
            url: str = i.attributes['href']  # type: ignore[assignment]
            # 'a' always has 'href'.
            related_subcategories.append(
                Subcategory(
                    raw_source=i.html or '',
                    id=int(url.split('/')[-2]),
                    type=subcategory_type,
                    name=i.css_first('div.counter-param').text().strip(),
                    offers_amount=int(i.css_first('div.counter-value').text().strip()),
                )
            )

        subcategory_id = int(subcategory_id_str.split('-')[-1])

        lot_fields_div = self.tree.css_first('div.lot-fields', strict=False)
        structure: SubcategoryStructure | None = None
        if lot_fields_div is not None:
            field_schema = OfferFieldsParser.parse_field_schema(lot_fields_div)
            structure = SubcategoryStructure(
                raw_source=lot_fields_div.html or '',
                subcategory_id=subcategory_id,
                fields={f.id: f for f in field_schema},
            )

        offers = (
            OfferPreviewsParser(
                showcase.html or '',
                options=self.options.offer_previews_parsing_options,
            ).parse()
            or None
        )

        # For CHIPS subcategories without an authoritative ``lot-fields`` block,
        # build a synthetic structure from the previews' ``other_data`` if the
        # caller opted in. OFFERS subcategories without lot-fields don't carry
        # structured ``other_data`` worth synthesizing from.
        if (
            structure is None
            and subcategory_type is SubcategoryType.CHIPS
            and self.options.fallback_structure_from_chips_offers
        ):
            structure = _synthesize_chips_structure(
                subcategory_id=subcategory_id,
                offers=offers or [],
            )

        return SubcategoryPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                self.tree.css_first('header').html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                self.tree.css_first('body').attributes['data-app-data'] or '',
                options=self.options.app_data_parsing_options,
            ).parse(),
            category_id=int(
                showcase.attributes['data-game']  # type: ignore[arg-type] # always has data-game
            ),
            subcategory_id=subcategory_id,
            subcategory_type=subcategory_type,
            related_subcategories=related_subcategories or None,
            offers=offers,
            structure=structure,
        )
