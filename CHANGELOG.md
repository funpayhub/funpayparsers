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

- Members of `funpayparsers.types.enums.SubcategoryType` and `funpayparsers.types.enums.Language` now use frozen 
dataclasses as their values instead of relying on custom `__new__` logic in Enums.
- Accessing enum fields now requires `.value`, e.g.:
  ```python
  Language.RU.value.url_alias
  ``
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