from __future__ import annotations


__all__ = ('SecurityChallengeParser', 'SecurityChallengeParsingOptions')


import re
import hashlib
from urllib.parse import urlparse
from dataclasses import dataclass

from selectolax.lexbor import LexborNode

from funpayparsers.types.security import (
    SecurityChallenge,
    SecurityChallengeKind,
    SecurityChallengeField,
)
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser


_TWO_FACTOR_FIELD = 'twofactor_code'
_PHONE_CHECK_PATH = '/ipChallengeCheck'
_PHONE_LABEL = 'телефон'
_NOT_AN_ANSWER = frozenset({'hidden', 'submit', 'button'})


@dataclass(frozen=True)
class SecurityChallengeParsingOptions(ParsingOptions):
    """Options class for ``SecurityChallengeParser``."""

    ...


class SecurityChallengeParser(
    FunPayHTMLObjectParser[SecurityChallenge, SecurityChallengeParsingOptions],
):
    """
    Class for parsing security pages that stand between a login and the account.

    Possible locations:
        - 2FA code page (`https://funpay.com/security/twoFactorLogin`): one input
          ``twofactor_code``, no form ``action``.
        - Last digits of a phone (`https://funpay.com/security/ipChallenge`): one input
          named ``0``, the masked phone in its addon, ``action`` is ``ipChallengeCheck``.

    Any other page with a form is returned as ``SecurityChallengeKind.UNKNOWN`` with its
    fields read from the page. A page without a form gives no fields.
    """

    def _parse(self) -> SecurityChallenge:
        form = self.tree.css_first('form', strict=False, default=None)
        fields = tuple(self._fields(form)) if form is not None else ()
        action = (form.attributes.get('action') or None) if form is not None else None
        title = _text(self.tree.css_first('h1', strict=False, default=None))
        hint = ' '.join(
            text
            for p in self.tree.css('#content p, .security-challenge p')
            if (text := _text(p))
        )
        return SecurityChallenge(
            raw_source=self.raw_source,
            kind=_kind(fields, action),
            title=title,
            hint=hint,
            action=action,
            fields=fields,
            shape_hash=_shape_hash(title, hint, action, fields),
        )

    def _fields(self, form: LexborNode) -> list[SecurityChallengeField]:
        result: list[SecurityChallengeField] = []
        for node in form.css('input'):
            name = node.attributes.get('name')
            input_type = (node.attributes.get('type') or 'text').lower()
            if not name or input_type in _NOT_AN_ANSWER:
                continue
            placeholder = node.attributes.get('placeholder') or ''
            result.append(
                SecurityChallengeField(
                    raw_source=node.html or '',
                    name=name,
                    label=_label_of(node),
                    placeholder=placeholder,
                    input_type=input_type,
                    length=sum(c.isdigit() for c in placeholder) or None,
                ),
            )
        return result


def _text(node: LexborNode | None) -> str:
    return ' '.join(node.text(strip=True).split()) if node is not None else ''


def _label_of(node: LexborNode) -> str:
    """Addon next to the input, else a ``<label>`` of its group, else empty."""
    parent = node.parent
    if parent is None:
        return ''
    addon = parent.css_first('.input-group-addon', strict=False, default=None)
    if addon is not None:
        return _text(addon)
    return _text(parent.css_first('label', strict=False, default=None))


def _kind(
    fields: tuple[SecurityChallengeField, ...],
    action: str | None,
) -> SecurityChallengeKind:
    if [f.name for f in fields] == [_TWO_FACTOR_FIELD]:
        return SecurityChallengeKind.TWO_FACTOR
    path = urlparse(action).path if action else ''
    if (
        len(fields) == 1
        and path.endswith(_PHONE_CHECK_PATH)
        and fields[0].label.lower().startswith(_PHONE_LABEL)
    ):
        return SecurityChallengeKind.PHONE_DIGITS
    return SecurityChallengeKind.UNKNOWN


def _shape(text: str) -> str:
    """Words only: digits, masks and a user's phone must not change the form's identity."""
    return re.sub(r'\s+', ' ', re.sub(r'[\d*+#]+', '#', text.lower())).strip()


def _shape_hash(
    title: str,
    hint: str,
    action: str | None,
    fields: tuple[SecurityChallengeField, ...],
) -> str:
    parts = [
        _shape(title),
        _shape(hint),
        urlparse(action).path if action else '',
        *(
            f'{_shape(f.name)}:{f.input_type}:{_shape(f.label)}:{f.length or 0}'
            for f in fields
        ),
    ]
    return hashlib.sha256('|'.join(parts).encode()).hexdigest()[:16]
