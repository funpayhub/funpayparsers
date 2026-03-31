from __future__ import annotations

import os

import pytest

from funpayparsers.types.enums import SubcategoryFieldType
from funpayparsers.types.subcategory_structure import SubcategoryFieldDef, SubcategoryStructure
from funpayparsers.parsers.offer_fields_parser import OfferFieldsParser, OfferFieldsParsingOptions
from funpayparsers.parsers.page_parsers.offer_page_parser import (
    OfferPageParser,
    OfferPageParsingOptions,
)


_HTML_DIR = os.path.join(os.path.dirname(__file__), '..', '..')


def _load(name: str) -> str:
    with open(os.path.join(_HTML_DIR, name), encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope='module')
def sub1_structure():
    fields = OfferFieldsParser(
        _load('subcategory1-item.html'),
        options=OfferFieldsParsingOptions(empty_raw_source=True),
    ).parse()
    return SubcategoryStructure.from_offer_fields(fields)


@pytest.fixture(scope='module')
def sub1_offer_page_no_struct():
    return OfferPageParser(
        _load('subcategory1-offer.html'),
        options=OfferPageParsingOptions(empty_raw_source=True),
    ).parse()


@pytest.fixture(scope='module')
def sub1_offer_page_with_struct(sub1_structure):
    return OfferPageParser(
        _load('subcategory1-offer.html'),
        options=OfferPageParsingOptions(
            empty_raw_source=True,
            subcategory_structure=sub1_structure,
        ),
    ).parse()


# ---------------------------------------------------------------------------
# fields dict (label → value)
# ---------------------------------------------------------------------------

def test_fields_contains_arena(sub1_offer_page_no_struct):
    assert 'Арена' in sub1_offer_page_no_struct.fields
    assert sub1_offer_page_no_struct.fields['Арена'] == '15'


def test_fields_contains_level(sub1_offer_page_no_struct):
    assert 'Уровень' in sub1_offer_page_no_struct.fields


# ---------------------------------------------------------------------------
# param_images
# ---------------------------------------------------------------------------

def test_param_images_extracted(sub1_offer_page_no_struct):
    assert len(sub1_offer_page_no_struct.param_images) > 0
    for url in sub1_offer_page_no_struct.param_images:
        assert url.startswith('http')


# ---------------------------------------------------------------------------
# structured_fields — None without structure
# ---------------------------------------------------------------------------

def test_structured_fields_none_without_structure(sub1_offer_page_no_struct):
    assert sub1_offer_page_no_struct.structured_fields is None


# ---------------------------------------------------------------------------
# structured_fields — populated with structure
# ---------------------------------------------------------------------------

def test_structured_fields_arena(sub1_offer_page_with_struct):
    sf = sub1_offer_page_with_struct.structured_fields
    assert sf is not None
    assert 'arena' in sf
    assert sf['arena'] == '15'


def test_structured_fields_level(sub1_offer_page_with_struct):
    sf = sub1_offer_page_with_struct.structured_fields
    assert sf is not None
    assert 'level' in sf


def test_structured_fields_no_image_keys(sub1_offer_page_with_struct):
    # Image param-items should NOT appear in structured_fields
    sf = sub1_offer_page_with_struct.structured_fields
    assert sf is not None
    assert 'images' not in sf


# ---------------------------------------------------------------------------
# Subcategory 3 (chips) — no offer_id in offer HTML, param_images empty
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def sub3_offer_page():
    return OfferPageParser(
        _load('subcategory3-offer.html'),
        options=OfferPageParsingOptions(empty_raw_source=True),
    ).parse()


def test_sub3_fields_contains_server(sub3_offer_page):
    assert 'Сервер' in sub3_offer_page.fields


def test_sub3_structured_fields_none(sub3_offer_page):
    assert sub3_offer_page.structured_fields is None
