from __future__ import annotations

from funpayparsers.types.offers import OfferFields
from funpayparsers.parsers.offer_fields_parser import (
    OfferFieldsParser,
    OfferFieldsParsingOptions,
)


OPTIONS = OfferFieldsParsingOptions(empty_raw_source=True)


lot_fields_html = """
<div class="page-content">
    <form action="https://funpay.com/lots/offerSave" method="post" class="form-offer-editor">
        <input type="hidden" name="csrf_token" value="CSRFTOKEN">
        <input type="hidden" name="form_created_at" value="1234567890">
        <input type="hidden" name="offer_id" value="0">
        <input type="hidden" name="node_id" value="2875">
        <input type="hidden" name="location" value="">
        <input type="hidden" name="deleted" value="">
    
        <div class="lot-fields live" data-fields="[{&quot;id&quot;:&quot;summary&quot;,&quot;type&quot;:2,&quot;conditions&quot;:[]},{&quot;id&quot;:&quot;desc&quot;,&quot;type&quot;:3,&quot;conditions&quot;:[]},{&quot;id&quot;:&quot;payment_msg&quot;,&quot;type&quot;:3,&quot;conditions&quot;:[]}]">
    
            <div class="lot-fields-multilingual">
                <ul class="nav nav-tabs">
                    <li class="js-locale-switcher active" data-locale="ru">
                        <a href="javascript:void(0)">По-русски</a>
                    </li>
                    <li class="js-locale-switcher" data-locale="en">
                        <a href="javascript:void(0)">По-английски</a>
                    </li>
                </ul>
                <div class="form-group lot-field bg-light-color modal-custom-bg-block modal-custom-bg-block-top" data-locale="ru" data-id="summary">
                    <label class="control-label">Краткое описание</label>
                    <input type="text" class="form-control lot-field-input" name="fields[summary][ru]" value="RuSummary">
                    <p class="help-block">Отображается прямо в таблице</p>
                </div>
                <div class="form-group lot-field bg-light-color modal-custom-bg-block hidden" data-locale="en" data-id="summary">
                    <label class="control-label">Short description</label>
                    <input type="text" class="form-control lot-field-input" name="fields[summary][en]" value="">
                    <p class="help-block">Appears directly on the table</p>
                </div>
                <div class="form-group lot-field bg-light-color modal-custom-bg-block" data-locale="ru" data-id="desc">
                    <label class="control-label">Подробное описание</label>
                    <textarea class="form-control lot-field-input" name="fields[desc][ru]" rows="7">RuDescription</textarea>
                    <p class="help-block">Можно не заполнять</p>
                </div>
                <div class="form-group lot-field bg-light-color modal-custom-bg-block hidden" data-locale="en" data-id="desc">
                    <label class="control-label">Detailed description</label>
                    <textarea class="form-control lot-field-input" name="fields[desc][en]" rows="7"></textarea>
                    <p class="help-block">Optional</p>
                </div>
                <div class="form-group lot-field bg-light-color modal-custom-bg-block" data-locale="ru" data-id="payment_msg">
                    <label class="control-label">Сообщение покупателю после оплаты</label>
                    <textarea class="form-control lot-field-input" name="fields[payment_msg][ru]" rows="7"></textarea>
                    <p class="help-block">Можно не заполнять. Будет отправлено каждому покупателю.</p>
                </div>
                <div class="form-group lot-field bg-light-color modal-custom-bg-block hidden" data-locale="en" data-id="payment_msg">
                    <label class="control-label">Message to the buyer after payment</label>
                    <textarea class="form-control lot-field-input" name="fields[payment_msg][en]" rows="7"></textarea>
                    <p class="help-block">Optional. Will be sent to each buyer.</p>
                </div>
            </div>
    
        </div>
        <div class="form-group">
            <div class="checkbox">
                <label>
                    <input type="checkbox" name="auto_delivery"><i></i>Автоматическая выдача</label>
            </div>
        </div>
        <div class="auto-delivery-box hidden">
            <div class="form-group">
                <label class="control-label">Товары</label>
                <textarea class="form-control textarea-lot-secrets" name="secrets" rows="7" placeholder="Товар 1
    Товар 2
    Товар 3
    ..."></textarea>
                <p class="help-block">Одна строка — один товар. Выдаются сверху вниз, выданные удаляются. Используйте \n для переноса внутри товара.</p>
            </div>
        </div>
    
        <div class="form-group has-feedback w-200px">
            <label class="control-label">Цена за 1 шт.</label>
            <input type="text" class="form-control" name="price" value="" inputmode="decimal" autocomplete="off">
            <span class="form-control-feedback">₽</span>
        </div>
    
        <div class="form-group has-feedback w-200px">
            <label class="control-label">Наличие</label>
            <input type="text" class="form-control" name="amount" placeholder="1" value="" inputmode="decimal" autocomplete="off">
            <span class="form-control-feedback">шт.</span>
        </div>
    
        <div class="form-group js-calc-table hidden">
            <label>Цена для покупателей</label>
            <table class="table-buyers-prices">
                <tbody class="js-calc-table-body">
                </tbody>
            </table>
        </div>
    
        <div class="form-group">
            <div class="checkbox">
                <label>
                    <input type="checkbox" name="active" checked=""><i></i>Активное</label>
            </div>
        </div>
    
        <div class="margin-top">
            <button type="submit" class="btn btn-primary btn-block js-btn-save">Сохранить</button>
        </div>
    </form>
</div>
"""

lot_fields_obj = OfferFields(
    raw_source='',
    fields_dict={
        'csrf_token': 'CSRFTOKEN',
        'form_created_at': '1234567890',
        'offer_id': '0',
        'node_id': '2875',
        'location': '',
        'deleted': '',
        'fields[summary][ru]': 'RuSummary',
        'fields[summary][en]': '',
        'fields[desc][ru]': 'RuDescription',
        'fields[desc][en]': '',
        'fields[payment_msg][ru]': '',
        'fields[payment_msg][en]': '',
        'auto_delivery': '',
        'secrets': '',
        'price': '',
        'amount': '',
        'active': 'on'
    }
)


def test_lot_fields_parser():
    parser = OfferFieldsParser(lot_fields_html, options=OPTIONS)
    assert parser.parse() == lot_fields_obj