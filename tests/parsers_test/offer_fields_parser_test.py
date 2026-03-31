from __future__ import annotations

import os

import pytest

from funpayparsers.types.enums import SubcategoryFieldType
from funpayparsers.types.subcategory_structure import FieldCondition, SubcategoryFieldDef
from funpayparsers.parsers.offer_fields_parser import (
    OfferFieldsParser,
    OfferFieldsParsingOptions,
)


OPTIONS = OfferFieldsParsingOptions(empty_raw_source=True)

_HTML_DIR = os.path.join(os.path.dirname(__file__), '..', '..')


def _load(name: str) -> str:
    with open(os.path.join(_HTML_DIR, name), encoding='utf-8') as f:
        return f.read()


# ---------------------------------------------------------------------------
# Subcategory 1 (Clash Royale accounts, node 149)
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def sub1_fields():
    return OfferFieldsParser(_load('subcategory1-item.html'), options=OPTIONS).parse()


def test_sub1_subcategory_id(sub1_fields):
    assert sub1_fields.subcategory_id == 149


def test_sub1_field_schema_count(sub1_fields):
    # arena, level, cup, card, legcard, namechange, summary, desc, payment_msg, images
    assert len(sub1_fields.field_schema) == 10


def test_sub1_arena_field(sub1_fields):
    arena = sub1_fields.field_schema[0]
    assert arena.id == 'arena'
    assert arena.type == SubcategoryFieldType.NUMERIC_RANGE
    assert arena.label == 'Арена'
    assert arena.conditions == []
    assert arena.options is None


def test_sub1_namechange_field(sub1_fields):
    namechange = next(f for f in sub1_fields.field_schema if f.id == 'namechange')
    assert namechange.type == SubcategoryFieldType.DROPDOWN
    assert namechange.options is not None
    assert 'Есть' in namechange.options
    assert 'Нет' in namechange.options


def test_sub1_summary_field(sub1_fields):
    summary = next(f for f in sub1_fields.field_schema if f.id == 'summary')
    assert summary.type == SubcategoryFieldType.TEXT
    assert summary.options is None


def test_sub1_images_field(sub1_fields):
    images = next(f for f in sub1_fields.field_schema if f.id == 'images')
    assert images.type == SubcategoryFieldType.IMAGES
    assert images.options is None


# ---------------------------------------------------------------------------
# Subcategory 2 (Clash Royale gems, node 973) — conditional fields
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def sub2_fields():
    return OfferFieldsParser(_load('subcategory2-item.html'), options=OPTIONS).parse()


def test_sub2_subcategory_id(sub2_fields):
    assert sub2_fields.subcategory_id == 973


def test_sub2_quantity_is_select(sub2_fields):
    quantity = next(f for f in sub2_fields.field_schema if f.id == 'quantity')
    assert quantity.type == SubcategoryFieldType.SELECT
    assert quantity.options is not None
    assert len(quantity.options) > 0


def test_sub2_quantity2_conditions(sub2_fields):
    quantity2 = next(f for f in sub2_fields.field_schema if f.id == 'quantity2')
    assert len(quantity2.conditions) == 1
    cond = quantity2.conditions[0]
    assert cond.field_id == 'quantity'
    assert 'другое количество' in cond.values


def test_sub2_special_conditions(sub2_fields):
    special = next(f for f in sub2_fields.field_schema if f.id == 'special')
    assert len(special.conditions) == 1
    cond = special.conditions[0]
    assert cond.field_id == 'quantity'
    assert 'особая акция' in cond.values


# ---------------------------------------------------------------------------
# Subcategory 3 (Lineage 2 chips) — currency offer, no lot-fields
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def sub3_fields():
    return OfferFieldsParser(_load('subcategory3-item.html'), options=OPTIONS).parse()


def test_sub3_is_currency(sub3_fields):
    assert sub3_fields.is_currency is True


def test_sub3_field_schema_empty(sub3_fields):
    assert sub3_fields.field_schema == []


# ---------------------------------------------------------------------------
# SubcategoryStructure.from_offer_fields
# ---------------------------------------------------------------------------

def test_structure_from_offer_fields(sub1_fields):
    from funpayparsers.types.subcategory_structure import SubcategoryStructure

    struct = SubcategoryStructure.from_offer_fields(sub1_fields)
    assert struct.subcategory_id == 149
    assert 'arena' in struct.field_map
    assert struct.field_map['arena'].label == 'Арена'
    assert 'Арена' in struct.label_map
    assert struct.label_map['Арена'] == 'arena'


# ---------------------------------------------------------------------------
# Inline HTML — conditions with list key
# ---------------------------------------------------------------------------

_INLINE_HTML = """
<div class="page-content">
  <form action="https://funpay.com/lots/offerSave" method="post">
    <input type="hidden" name="csrf_token" value="tok">
    <input type="hidden" name="node_id" value="42">
    <div class="lot-fields" data-fields="[
      {&quot;id&quot;:&quot;region&quot;,&quot;type&quot;:4,&quot;conditions&quot;:[]},
      {&quot;id&quot;:&quot;rank&quot;,&quot;type&quot;:1,&quot;conditions&quot;:[{&quot;id&quot;:&quot;region&quot;,&quot;list&quot;:[&quot;eu&quot;,&quot;ru&quot;]}]}
    ]">
      <div class="form-group lot-field" data-id="region">
        <label class="control-label">Регион</label>
        <select class="form-control lot-field-input" name="fields[region]">
          <option value=""></option>
          <option value="eu">EU</option>
          <option value="ru">RU</option>
        </select>
      </div>
      <div class="form-group lot-field" data-id="rank">
        <label class="control-label">Ранг</label>
        <input type="text" name="fields[rank]">
      </div>
    </div>
  </form>
</div>
"""


def test_inline_conditions_list_key():
    result = OfferFieldsParser(_INLINE_HTML, options=OPTIONS).parse()
    assert result.subcategory_id == 42
    assert len(result.field_schema) == 2

    region = result.field_schema[0]
    assert region.id == 'region'
    assert region.type == SubcategoryFieldType.SELECT
    assert region.options == ['eu', 'ru']
    assert region.conditions == []

    rank = result.field_schema[1]
    assert rank.id == 'rank'
    assert rank.type == SubcategoryFieldType.NUMERIC_RANGE
    assert rank.conditions == [FieldCondition(field_id='region', values=['eu', 'ru'])]
    assert rank.options is None
