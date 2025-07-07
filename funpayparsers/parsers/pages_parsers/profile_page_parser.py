__all__ = ('ProfilePageParserOptions', 'ProfilePageParser')


from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, FunPayObjectParserOptions
from funpayparsers.parsers.reviews_parser import ReviewsParser, ReviewsParserOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParserOptions
from funpayparsers.parsers.page_header_parser import PageHeaderParser, PageHeaderParserOptions
from funpayparsers.parsers.offer_previews_parser import OfferPreviewsParser, OfferPreviewsParserOptions
from funpayparsers.parsers.rating_parser import UserRatingParser, UserRatingParserOptions
from funpayparsers.parsers.chat_parser import ChatParser, ChatParserOptions
from funpayparsers.parsers.badge_parser import UserBadgeParser, UserBadgeParserOptions
from funpayparsers.parsers.utils import extract_css_url
from funpayparsers.types.pages.profile_page import ProfilePage
from funpayparsers.types.enums import BadgeType, SubcategoryType


@dataclass(frozen=True)
class ProfilePageParserOptions(FunPayObjectParserOptions):
    page_header_parser_options: PageHeaderParserOptions = PageHeaderParserOptions()
    app_data_parser_options: AppDataParserOptions = AppDataParserOptions()
    user_rating_parser_options: UserRatingParserOptions = UserRatingParserOptions()
    offer_previews_parser_options: OfferPreviewsParserOptions = OfferPreviewsParserOptions()
    user_badge_parser_options: UserBadgeParserOptions = UserBadgeParserOptions()
    chat_parser_options: ChatParserOptions = ChatParserOptions()
    reviews_parser_options: ReviewsParserOptions = ReviewsParserOptions()


class ProfilePageParser(FunPayHTMLObjectParser[ProfilePage, ProfilePageParserOptions]):
    """"
    Class for parsing FunPay profile page.
    Possible locations:
        - https://funpay.com/users/<user_id>/
    """

    def _parse(self):
        header = self.tree.css_first('header')
        app_data = self.tree.css_first('body').attributes['data-app-data']

        profile_header = self.tree.css_first('div.profile-header')
        reg_date_text_div = profile_header.css('div.param-item')
        rating_div = profile_header.css_first('div.profile-header-col-rating')
        offer_divs = self.tree.css('div.mb20 div.offer')
        chat_div = self.tree.css('div.chat')
        reviews_div = self.tree.css('div.offer:has(div.dyn-table-body)')

        badges = [UserBadgeParser(i.html, options=self.options.user_badge_parser_options).parse()
                  for i in profile_header.css('small.user-badges > span')]
        for i in badges:
            if i.type is BadgeType.BANNED:
                banned = True
                badges.remove(i)
                badge = badges[0] if badges else None
                break
        else:
            banned = False
            badge = badges[0] if badges else None

        if offer_divs:
            offers = {SubcategoryType.COMMON: {}, SubcategoryType.CURRENCY: {}, SubcategoryType.UNKNOWN: {}}
            for offer_div in offer_divs:
                url = offer_div.css_first('div.offer-list-title a').attributes['href']
                id_ = int(url.split('/')[-2])
                offers_objs = OfferPreviewsParser(offer_div.html, options=self.options.offer_previews_parser_options).parse()
                offers[SubcategoryType.get_by_url(url)][id_] = offers_objs
        else:
            offers = None

        return ProfilePage(
            raw_source=self.tree.html,
            header=PageHeaderParser(header.html, options=self.options.page_header_parser_options).parse(),
            app_data=AppDataParser(app_data, options=self.options.app_data_parser_options).parse(),
            user_id=int(self.tree.css_first('head > link[rel="canonical"]').attributes['href'].split('/')[-2]),
            username=profile_header.css_first('span.mr4').text().strip(),
            badge=badge,
            achievements=...,
            avatar_url=extract_css_url(self.tree.css_first('div.avatar-photo').attributes['style']),
            online='online' in profile_header.css_first('h1.mb40').attributes['class'],
            banned=banned,
            registration_date_text=reg_date_text_div[0].text(separator='\n', strip=True).strip().split('\n')[-2],
            status_text=profile_header.css_first('span.media-user-status').text().strip() if not banned else None,
            rating=UserRatingParser(rating_div.html, options=self.options.user_rating_parser_options).parse() if rating_div else None,
            offers=offers,
            chat=ChatParser(chat_div[0].html, options=self.options.chat_parser_options).parse() if chat_div else None,
            reviews=ReviewsParser(reviews_div[0].html, options=self.options.reviews_parser_options).parse() if reviews_div else [],
        )
