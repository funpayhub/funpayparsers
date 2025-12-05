# FunPage Parsers Release Notes

## FunPay Parsers 0.1.1

### Bug fixes

- Fixed `funpayparsers.parsers.page_parsers.SubcategoryPageParser`: fields `category_id` and `subcategory_id`.


## FunPay Parsers 0.2.0

### Features

- Added `funpayparsers.message_type_re`: list of compiled regular expressions for FunPay
system messages.
- Added `funpayparsers.types.enums.MessageType`: FunPay system message types enumeration.
- Added `funpayparsers.types.messages.Message.type`: field, that contains message type.
- `funpayparsers.types.enums.SubcategoryType` members now have 2 fields:
`showcase_alias` and `url_alias`. Using `value` of a member marked as deprecated.
- `funpayparsers.types.enums.Language` members now have 3 fields:
`url_alias`, `appdata_alias` and `header_menu_css_class`.
Using `value` of a member marked as deprecated.

### Bug fixes

- `funpayparsers.types.messages.Message.chat_name` now has type `str | None` instead of `str`.

### Deprecations

- Using `value` of `funpayparsers.types.enums.SubcategoryType` members is deprecated.
Use `showcase_alias` or `url_alias` of members instead.
- Using `value` of `funpayparsers.types.enums.Language` members is deprecated.
Use `url_alias`, `appdata_alias` or `header_menu_css_class` of members instead.


## FunPay Parsers 0.3.0

### Changes

- Members of `funpayparsers.types.enums.SubcategoryType` and `funpayparsers.types.enums.Language` now use frozen 
dataclasses as their values instead of relying on custom `__new__` logic in Enums.
- Accessing enum fields now requires `.value`, e.g.:
  ```python
  Language.RU.value.url_alias
  ```
- All `get_by_...` class methods in all enums have been converted to `@staticmethod`s.

> **Note**
>
> These changes were introduced to improve code maintainability and better align with the 
> Single Responsibility Principle (SRP).
> While ideally the `get_by_...` logic would reside outside the Enums (in dedicated resolvers),
> keeping them as static methods within the enum classes is a deliberate compromise for simplicity — 
> given their limited number and scope.
>
> Using dataclasses for enum values simplifies internal logic, improves clarity, and provides better support 
> for type checkers like `mypy`.
>
> This design is currently considered a balanced trade-off between architectural purity and practical readability.


## FunPay Parsers 0.3.1

### Features

- Added `@classmethod` `from_raw_source` to `FunPayObject`. Raises `NotImplementedError` by default.
- Implemented `from_raw_source` in all page-types.
- Added `timestamp` property to `funpayparsers.types.Message`.

### Improvements

- Improved ``funpayparsers.parsers.utils.parse_date_string``: added new patterns of dates.
- Improved ``funpayparsers.parsers.utils.resolve_messages_senders``: field `send_date_text` of heading message 
now propagates on messages below it.


## FunPay Parsers 0.4.0

### Features

- Added new object `funpayparses.types.messages.MessageMeta` and related parser 
`funpayparsers.parsers.message_meta_parser.MessageMetaParser`. `MessageMeta` contains meta info about message, such is
message type and mentioned seller / buyer / admin / order (if it is system message). `MessageMetaParser` accepts inner
html of message (inner html of `div.chat-msg-text`) and returns `MessageMeta` object.

### Changes

- `funpayparsers.types.messages.Message.type` moved to `funpayparsers.types.messages.Message.meta.type`


### Fixes

- `funpayparsers.parsers.messages_parser.MessagesParser` doesn't strip message texts anymore.


## FunPay Parsers 0.4.1

### Fixes

- `funpayparsers.parsers.page_parsers.subcategory_page_parser.SubCategoryPageParser` now can parse anonymous response.


### Improvements

- `funpayparsers.exceptions.ParsingError` now shorts HTML in error message if it longer than 500 symbols.


## FunPay Parsers 0.4.2

### Fixes

- `funpayparsers.parsers.utils.parse_date_string` now respects machines timezone.


## FunPay Parsers 0.4.3


### Features

- Added property `price` to `funpayparsers.types.offers.OfferFields`.

### Fixes

- `funpayparsers.parsers.offer_fields_parser.OfferFieldsParser` now can parse offer fields from full page HTML.


## FunPay Parsers 0.5.0


### Features

- Added new badge type: `funpayparsers.types.enums.BadgeType.NOT_ACTIVATED` (#88)
- Improved `funpayparsers.types.offers.OfferFields`
  - Added new methods:
    - Method `.convert_to_currency` that converts `OfferFields` instance to *currency-type* fields.
    - Method `.convert_to_common` that converts `OfferFields` instance to *common-type* fields.
    - Method `.get_currency_amount` that returns currency amount of specified currency. Applicable for 
*currency-type* offers only.
    - Method `.set_currency_amount` that sets currency amount of specified currency. Applicable for 
*currency-type* offers only.
    - Method `.get_currency_price` that returns currency price of specified currency. Applicable for 
*currency-type* offers only.
    - Method `.set_currency_price` that sets currency price of specified currency. Applicable for 
*currency-type* offers only.
    - Method `.get_currency_status` that returns currency active status of specified currency. Applicable for 
*currency-type* offers only.
    - Method `.set_currency_status` that sets currency active status of specified currency. Applicable for 
*currency-type* offers only.
  - Added new `@property`'s:
    - Property `.is_currency`, that indicates whether `OfferFields` instance is *currency-type* or not.
    - Property `.is_common`, that indicates whether `OfferFields` instance is *common-type* or not.
    - Property `.subcategory_id` (field name: `chip` for *currency-type*, `node_id` for *common-type* offers).
    - Property `.category_id` (field name: `game`, applicable for *currency-type* offers only).
    - Property `.min_sum` (field name: `chip_min_sum`, applicable for *currency-type* offers only).
    - Property `.offer_id` (field name: `offer_id`, applicable for *common-type* offers only).
    - Property `.price` (field name: `price`, applicable for *common-type* offers only).
  - Added type checks to existing `@property`'s. Some properties are applicable for *currency-type* offers only, some
for *common-type* offers only.
  - Improved doc-strings.
- Added timestamp `@property`'s to objects with date fields (returns `0` if an error occurred while parsing date text):
  - `funpayparsers.types.chat.PrivateChatInfo.registration_timestamp`.
  - `funpayparsers.types.finances.TransactionPreview.timestamp`.
  - `funpayparsers.types.offers.OfferSeller.registration_timestamp`.
  - `funpayparsers.types.reviews.Review.timestamp` (available only for owned reviews).
    
### Improvements

- `funpayparsers.types.offers.OfferFields.set_field` now automatically converts value into `str`.
- `funpayparsers.types.offers.OfferFields` now automatically removes `csrf_token` field after initialization
  (in `__post_init__`).
- Improved `funpayparsers.parsers.utils.parse_date_string`:
  - Removed redundant regular expressions.
  - Optimized existing regular expressions.
  - Added support of new time formats (review time format for all languages). 
  - Added related tests.


### Changes

- Removed `funpayparsers.types.offers.OfferFields.csrf_token`.
- `funpayparsers.types.offers.OfferSeller.register_date_text` changed to 
`funpayparsers.types.offers.OfferSeller.registration_date_text`.
- `funpayparsers.types.reviews.Review.time_ago_str` changed to `funpayparsers.types.reviews.Review.date_text`.


## FunPay Parsers 0.5.1

### Fixes

- `funpayparsers.parsers.page_parsers.transactions_page_parser` updated for new transactions page.


## FunPay Parsers 0.5.2

### Features

- Added `sales_available` field to `funpayparsers.types.common_page_elements.PageHeader`.
- Added parsing of `sales_available` field.



## FunPay Parsers 0.5.3

### Features

- Added `logout_token` to `funpayparsers.types.common_page_elements.PageHeader`.
- Added parsing of `logout_token` field.


## FunPay Parsers 0.5.4

### Features

- Added `funpayparsers.types.settings.Settings` type.
- Added `funpayparsers.types.pages.settings_page.SettingsPage` type.
- Added `funpayparsers.parsers.page_parsers.settings_page_parser.SettingsPageParser`.

# Fixes

- Added spaces to word separators in date parsing tests.
