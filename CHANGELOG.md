# FunPage Parsers Release Notes

## FunPay Parsers 0.1.1

### Bug fixes

- Fixed ``funpayparsers.parsers.page_parsers.SubcategoryPageParser``: fields ``category_id`` and ``subcategory_id``.


## FunPay Parsers 0.1.2

### Features

- Added ``funpayparsers.message_type_re``: list of compiled regular expressions for FunPay
system messages.
- Added ``funpayparsers.types.enums.MessageType``: FunPay system message types enumeration.
- Added ``funpayparsers.types.messages.Message.type``: field, that contains message type.
- ``funpayparsers.types.enums.SubcategoryType`` members now have 2 fields:
``showcase_alias`` and ``url_alias``. Using ``value`` of a member marked as deprecated.
- ``funpayparsers.types.enums.Language`` members now have 3 fields:
``url_alias``, ``appdata_alias`` and ``header_menu_css_class``.
Using ``value`` of a member marked as deprecated.

### Bug fixes

- ``funpayparsers.types.messages.Message.chat_name`` now has type ``str | None`` instead of ``str``.

### Deprecations

- Using ``value`` of ``funpayparsers.types.enums.SubcategoryType`` members is deprecated.
Use ``showcase_alias`` or ``url_alias`` of members instead.
- Using ``value`` of ``funpayparsers.types.enums.Language`` members is deprecated.
Use ``url_alias``, ``appdata_alias`` or ``header_menu_css_class`` of members instead.