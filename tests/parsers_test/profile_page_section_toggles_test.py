from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from funpayparsers.parsers.page_parsers.profile_page_parser import (
    ProfilePageParser,
    ProfilePageParsingOptions,
)


if TYPE_CHECKING:
    from funpayparsers.types.pages.profile_page import ProfilePage


PROFILE_HTML = """
<html>
<head><link rel="canonical" href="https://funpay.com/users/1234/"/></head>
<body data-app-data='{"locale": "ru", "csrf-token": "tok", "userId": 1234}'>
<header>
  <a class="dropdown-toggle menu-item-currencies">руб.</a>
  <a class="dropdown-toggle menu-item-langs"><i class="menu-icon menu-icon-lang-ru"></i></a>
</header>
<div class="profile-header">
  <h1 class="mb40 online"><span class="mr4">SomeSeller</span></h1>
  <div class="avatar-photo" style="background-image: url(/img/a.jpg);"></div>
  <span class="media-user-status">Online</span>
  <small class="user-badges"></small>
  <div class="param-item">
    <div>Registered</div>
    <div>15 August 2015, 18:01</div>
    <div>10 years ago</div>
  </div>
</div>

<div class="param-item mb10">
  <div class="rating-value"><span class="big">4.9</span></div>
  <div class="mb5">1049 reviews</div>
  <div class="rating-full-item1">
    <div class="rating-progress"><div style="width: 1%"></div></div>
  </div>
  <div class="rating-full-item2">
    <div class="rating-progress"><div style="width: 2%"></div></div>
  </div>
  <div class="rating-full-item3">
    <div class="rating-progress"><div style="width: 3%"></div></div>
  </div>
  <div class="rating-full-item4">
    <div class="rating-progress"><div style="width: 4%"></div></div>
  </div>
  <div class="rating-full-item5">
    <div class="rating-progress"><div style="width: 90%"></div></div>
  </div>
</div>

<div class="achievement-item"><i class="fas fa-medal"></i>Achievement</div>

<div class="mb20">
  <div class="offer">
    <div class="offer-list-title"><a href="https://funpay.com/lots/81/"></a></div>
    <a href="https://funpay.com/lots/offer?id=12345" class="tc-item" data-online="1"
       data-auto="1" data-user="1234">
      <div class="tc-desc"><div class="tc-desc-text">Lot Description</div></div>
      <div class="tc-amount hidden-xxs">1</div>
      <div class="tc-price" data-s="3499.79"><div>3500 <span class="unit">R</span></div></div>
    </a>
  </div>
</div>

<div class="offer"><div class="dyn-table-body"></div></div>

<div class="chat">
  <div class="chat-header"></div>
  <div class="chat-message-list"></div>
</div>
</body>
</html>
"""

HEAD_ONLY = ProfilePageParsingOptions(
    parse_offers=False,
    parse_reviews=False,
    parse_chat=False,
    parse_achievements=False,
)


def parse(options: ProfilePageParsingOptions | None = None) -> ProfilePage:
    return ProfilePageParser(PROFILE_HTML, options=options).parse()


def test_all_sections_are_parsed_by_default():
    page = parse()

    assert page.offers is not None
    assert page.reviews is not None
    assert page.chat is not None
    assert page.achievements != []


def test_disabled_sections_are_empty():
    page = parse(HEAD_ONLY)

    assert page.offers is None
    assert page.reviews is None
    assert page.chat is None
    assert page.achievements == []


def test_head_is_identical_with_sections_disabled():
    full, head_only = parse(), parse(HEAD_ONLY)

    assert head_only.user_id == full.user_id
    assert head_only.username == full.username
    assert head_only.online == full.online
    assert head_only.banned == full.banned
    assert head_only.avatar_url == full.avatar_url
    assert head_only.status_text == full.status_text
    assert head_only.registration_date_text == full.registration_date_text


def test_rating_survives_reviews_being_disabled():
    # The rating comes from the rating block, not from the review list, so
    # `parse_reviews=False` must not take it away.
    page = parse(ProfilePageParsingOptions(parse_reviews=False))

    assert page.reviews is None
    assert page.rating is not None
    assert page.rating.stars == 4.9
    assert page.rating.reviews_amount == 1049


@pytest.mark.parametrize(
    ('option', 'attr', 'empty'),
    [
        ('parse_offers', 'offers', None),
        ('parse_reviews', 'reviews', None),
        ('parse_chat', 'chat', None),
        ('parse_achievements', 'achievements', []),
    ],
)
def test_each_toggle_is_independent(option: str, attr: str, empty: object):
    page = parse(ProfilePageParsingOptions(**{option: False}))

    assert getattr(page, attr) == empty
    for other, other_empty in [
        ('offers', None),
        ('reviews', None),
        ('chat', None),
        ('achievements', []),
    ]:
        if other != attr:
            assert getattr(page, other) != other_empty
