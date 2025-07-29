from __future__ import annotations

import re


__all__ = (
    'NEW_ORDER',
    'ORDER_CLOSED',
    'ORDER_CLOSED_BY_ADMIN',
    'ORDER_REOPENED',
    'ORDER_REFUNDED',
    'ORDER_PARTIALLY_REFUND',
    'NEW_FEEDBACK',
    'FEEDBACK_CHANGED',
    'FEEDBACK_DELETED',
    'NEW_FEEDBACK_REPLY',
    'FEEDBACK_REPLY_CHANGED',
    'FEEDBACK_REPLY_DELETED',
    'ORDER_ID',
    'USERNAME',
)


_oirs = '[A-Z0-9]{8}'  # order id RE string
_urs = '[a-zA-Z0-9]{3,20}'  # username RE string
_f_dict = {'urs': _urs, 'oirs': _oirs}


NEW_ORDER = re.compile(
    r'(?m:Покупатель (?P<u>%(urs)s) оплатил заказ #%(oirs)s\. .+\n'
    r'(?P=u), не забудьте потом нажать кнопку «Подтвердить выполнение заказа»\.)|'
    r'(?m:The buyer (?P<e_u>%(urs)s) has paid for order #%(oirs)s\. .+\n'
    r'(?P=e_u), do not forget to press the «Confirm order fulfilment» button once you finish.)'
    % _f_dict
)
"""
Покупатель <ИМЯ ПОКУПАТЕЛЯ> оплатил заказ #<ID ЗАКАЗА>. <НАЗВАНИЕ ЛОТА>.
<ИМЯ ПОКУПАТЕЛЯ>, не забудьте потом нажать кнопку «Подтвердить выполнение заказа».

The buyer <BUYER USERNAME> has paid for order #<ORDER ID>. Warface, <LOT NAME>
<BUYER USERNAME>, do not forget to press the «Confirm order fulfilment» button once you finish.
"""


ORDER_CLOSED = re.compile(
    r'(Покупатель %(urs)s подтвердил успешное выполнение заказа #%(oirs)s '
    r'и отправил деньги продавцу %(urs)s\.)|'
    r'(The buyer %(urs)s has confirmed that order #%(oirs)s has been '
    r'fulfilled successfully and that the seller %(urs)s has been paid\.)' % _f_dict
)
"""
Покупатель <ИМЯ ПОКУПАТЕЛЯ> подтвердил успешное выполнение заказа #<ID ЗАКАЗА> 
    и отправил деньги продавцу <ИМЯ ПРОДАВЦА>.

The buyer <BUYER USERNAME> has confirmed that order #<ORDER ID> has been fulfilled successfully 
    and that the seller <SELLER USERNAME> has been paid.
"""


ORDER_CLOSED_BY_ADMIN = re.compile(
    r'(Администратор %(urs)s подтвердил успешное выполнение '
    r'заказа #%(oirs)s и отправил деньги продавцу %(urs)s\.)|'
    r'(The administrator %(urs)s has confirmed that order '
    r'#%(oirs)s has been fulfilled successfully and that the seller '
    r'%(urs)s has been paid\.)' % _f_dict
)
"""
Администратор <ИМЯ АДМИНИСТРАТОРА> подтвердил успешное выполнение заказа #<ID ЗАКАЗА> 
    и отправил деньги продавцу <ИМЯ ПРОДАВЦА>.

The administrator <ADMIN USERNAME> has confirmed that order #<ORDER ID> has been fulfilled successfully 
    and that the seller <SELLER USERNAME> has been paid.
"""


ORDER_REOPENED = re.compile(
    r'(Заказ #%(oirs)s открыт повторно\.)|' r'(Order #%(oirs)s has been reopened\.)' % _f_dict
)
"""
Заказ #ORDERID открыт повторно.

Order #ORDERID has been reopened.
"""


ORDER_REFUNDED = re.compile(
    r'(Продавец %(urs)s вернул деньги покупателю %(urs)s по заказу #%(oirs)s\.)|'
    r'(The seller %(urs)s has refunded the buyer %(urs)s on order #%(oirs)s\.)' % _f_dict
)
"""
Продавец <ИМЯ ПРОДАВЦА> вернул деньги покупателю <ИМЯ ПОКУПАТЕЛЯ> по заказу #<ID ЗАКАЗА>.

The seller <SELLER USERNAME> has refunded the buyer <BUYER USERNAME> on order #<ORDER ID>.
"""


ORDER_PARTIALLY_REFUND = re.compile(
    r'(Часть средств по заказу #%(oirs)s возвращена покупателю\.)|'
    r'(A part of the funds pertaining to the order #%(oirs)s has been refunded\.)' % _f_dict
)
"""
Часть средств по заказу #ORDERID возвращена покупателю.

A part of the funds pertaining to the order #ORDERID has been refunded.
"""


NEW_FEEDBACK = re.compile(
    r'(Покупатель %(urs)s написал отзыв к заказу #%(oirs)s\.)|'
    r'(The buyer %(urs)s has given feedback to the order #%(oirs)s\.)' % _f_dict
)
"""
Покупатель <ИМЯ ПОКУПАТЕЛЯ> написал отзыв к заказу #<ID ЗАКАЗА>.

The buyer <BUYER USERNAME> has given feedback to the order #<ORDER ID>.
"""


FEEDBACK_CHANGED = re.compile(
    r'(Покупатель %(urs)s изменил отзыв к заказу #%(oirs)s\.)|'
    r'(The buyer %(urs)s has edited their feedback to the order #%(oirs)s\.)' % _f_dict
)
"""
Покупатель <ИМЯ ПОКУПАТЕЛЯ> изменил отзыв к заказу #<ID ЗАКАЗА>.

The buyer <BUYER USERNAME> has edited their feedback to the order #<ORDER ID>.
"""


FEEDBACK_DELETED = re.compile(
    r'(Покупатель %(urs)s удалил отзыв к заказу #%(oirs)s\.)|'
    r'(The buyer %(urs)s has deleted their feedback to the order #%(oirs)s\.)' % _f_dict
)
"""
Покупатель <ИМЯ ПОКУПАТЕЛЯ> удалил отзыв к заказу #<ID ЗАКАЗА>.

The buyer <BUYER USERNAME> has deleted their feedback to the order #<ORDER ID>.
"""


NEW_FEEDBACK_REPLY = re.compile(
    r'(Продавец %(urs)s ответил на отзыв к заказу #%(oirs)s\.)|'
    r'(The seller %(urs)s has replied to their feedback to the order #%(oirs)s\.)' % _f_dict
)
"""
Продавец <ИМЯ ПРОДАВЦА> ответил на отзыв к заказу #<ID ЗАКАЗА>.

The seller <SELLER USERNAME> has replied to their feedback to the order #<ORDER ID>.
"""


FEEDBACK_REPLY_CHANGED = re.compile(
    r'(Продавец %(urs)s изменил ответ на отзыв к заказу #%(oirs)s\.)|'
    r'(The seller %(urs)s has edited a reply to their feedback '
    r'to the order #%(oirs)s\.)' % _f_dict
)
"""
Продавец <ИМЯ ПРОДАВЦА> изменил ответ на отзыв к заказу #<ID ЗАКАЗА>.

The seller <SELLER USERNAME> has edited a reply to their feedback to the order #<ORDER ID>.
"""


FEEDBACK_REPLY_DELETED = re.compile(
    r'(Продавец %(urs)s удалил ответ на отзыв к заказу #%(oirs)s\.)|'
    r'(The seller %(urs)s has deleted a reply to their feedback '
    r'to the order #%(oirs)s\.)' % _f_dict
)
"""
Продавец <ИМЯ ПРОДАВЦА> удалил ответ на отзыв к заказу #<ID ЗАКАЗА>.

The seller <SELLER USERNAME> has deleted a reply to their feedback to the order #<ORDER ID>.
"""


ORDER_ID = re.compile(_oirs)
"""
Order ID compiled RE.
"""


USERNAME = re.compile(_urs)
"""
Username compiled RE.
"""
