from funpayparsers.parsers.reviews_parser import ReviewsParser, ReviewsParserOptions
from funpayparsers.types.review import Review
from funpayparsers.types.common import MoneyValue


OPTIONS = ReviewsParserOptions(empty_raw_source=True)


public_review_html = """
<div class="review-container">
  <div class="review-item">
    <div class="review-item-row">
      <div class="review-compiled-review">
        <div class="review-item-user">
          <div class="review-item-photo">
            <img src="/img/layout/avatar.png" alt="">
          </div>
          <div class="review-item-rating pull-right hidden-xs">
            <div class="rating">
              <div class="rating5"></div>
            </div>
          </div>
          <div class="review-item-date">2 месяца назад</div>
          <div class="review-item-detail">Game, 100 ₽</div>
          <div class="review-item-rating visible-xs">
            <div class="rating">
              <div class="rating5"></div>
            </div>
          </div>
        </div>
        <div class="review-item-text"> ReviewText </div>
      </div>
    </div>
    <div class="review-item-row">
      <div class="h5 mb5">Ответ продавца</div>
      <div class="review-item-answer review-compiled-reply">
        <div>ReviewReply</div>
      </div>
    </div>
  </div>
</div>
"""

public_review_obj = Review(
    raw_source='',
    rating=5,
    text='ReviewText',
    order_total=MoneyValue(
        raw_source='',
        value=100,
        character='₽'
    ),
    order_category='Game',
    sender_username=None,
    sender_id=None,
    sender_avatar_url=None,
    order_id=None,
    order_time_string='2 месяца назад',
    response='ReviewReply'
)


my_public_review_html = """
<div class="review-container">
  <div class="review-item">
    <div class="review-item-row">
      <div class="review-compiled-review">
        <div class="review-item-user">
          <div class="review-item-photo">
            <a href="https://funpay.com/users/54321/">
              <img src="/img/layout/avatar.png" alt="">
            </a>
          </div>
          <div class="review-item-rating pull-right hidden-xs">
            <div class="rating">
              <div class="rating3"></div>
            </div>
          </div>
          <div class="media-user-name">
            <a href="https://funpay.com/users/54321/">SenderUername</a>
          </div>
          <div class="review-item-order">
            <a href="https://funpay.com/orders/ABCDEFGH/">Заказ #ABCDEFGH</a>
          </div>
          <div class="review-item-date">20 января в 12:58, 3 месяца назад</div>
          <div class="review-item-detail">Game, 50 ₽</div>
          <div class="review-item-rating visible-xs">
            <div class="rating">
              <div class="rating3"></div>
            </div>
          </div>
        </div>
        <div class="review-item-text"> ReviewText </div>
      </div>
    </div>
    <div class="review-item-row">
      <div class="h5 mb5">Ответ продавца</div>
      <div class="review-item-answer review-compiled-reply">
        <div>ReviewReply️</div>
      </div>
    </div>
  </div>
</div>
"""

my_public_review_obj = Review(
    raw_source='',
    rating=3,
    text='ReviewText',
    order_total=MoneyValue(
        raw_source='',
        value=50,
        character='₽'
    ),
    order_category='Game',
    sender_username='SenderUername',
    sender_id=54321,
    sender_avatar_url='/img/layout/avatar.png',
    order_id='ABCDEFGH',
    order_time_string='20 января в 12:58, 3 месяца назад',
    response='ReviewReply'
)


order_page_review_html = """
<div class="review-container" data-order="ABCDEFGH" data-rating="1" data-rating-max="5">
  <div class="review-item">
    <div class="review-item-row" data-row="review" data-author="54321">
      <div class="review-compiled-review">
        <div class="review-item-user">
          <div class="review-item-photo">
            <a href="https://funpay.com/users/54321/">
              <img src="/img/layout/avatar.png" alt="">
            </a>
          </div>
          <div class="review-item-rating pull-right hidden-xs">
            <div class="rating">
              <div class="rating1"></div>
            </div>
          </div>
          <div class="review-item-date">2 месяца назад</div>
          <div class="review-item-detail">Game, 500 $</div>
          <div class="review-item-rating visible-xs">
            <div class="rating">
              <div class="rating1"></div>
            </div>
          </div>
        </div>
        <div class="review-item-text"> ReviewText </div>
      </div>
    </div>
    <div class="review-item-row" data-row="reply" data-author="12345">
      <div class="h5 mb5">Ответ продавца</div>
      <div class="review-item-answer review-compiled-reply">
        <div>ReviewReply️</div>
        <div class="review-controls">
          <button class="btn btn-primary btn-sm action" data-action="edit">Редактировать</button>
          <button class="btn btn-danger btn-sm action" data-action="delete">Удалить</button>
        </div>
      </div>
      <div class="review-item-answer-form review-editor-reply hidden">
        <div class="form-group">
          <textarea class="form-control" name="text" cols="30" rows="6">ReviewReply️️</textarea>
          <div class="help-form">Ваш ответ будет виден всем после публикации</div>
        </div>
        <div class="form-group">
          <button class="btn btn-primary action" data-action="save">Опубликовать</button>
        </div>
      </div>
    </div>
  </div>
</div>
"""


order_page_review_obj = Review(
    raw_source='',
    rating=1,
    text='ReviewText',
    order_total=MoneyValue(
        raw_source='',
        value=500,
        character='$'
    ),
    order_category='Game',
    sender_username=None,
    sender_id=54321,
    sender_avatar_url='/img/layout/avatar.png',
    order_id='ABCDEFGH',
    order_time_string='2 месяца назад',
    response='ReviewReply'
)


def test_public_reviews_parsing():
    parser = ReviewsParser(public_review_html, options=OPTIONS)
    assert parser.parse() == [public_review_obj]


def test_my_public_reviews_parsing():
    parser = ReviewsParser(my_public_review_html, options=OPTIONS)
    assert parser.parse() == [my_public_review_obj]


def test_order_page_review_parsing():
    parser = ReviewsParser(order_page_review_html, options=OPTIONS)
    assert parser.parse() == [order_page_review_obj]
