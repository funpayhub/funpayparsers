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