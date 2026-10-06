from __future__ import annotations


__all__ = ('SecurityChallengeKind', 'SecurityChallengeField', 'SecurityChallenge')


from enum import Enum
from urllib.parse import urlparse
from dataclasses import dataclass

from funpayparsers.types.base import FunPayObject


class SecurityChallengeKind(Enum):
    """What a security page asks for."""

    TWO_FACTOR = 'two_factor'
    """Authenticator app's 6-digit code (``https://funpay.com/security/twoFactorLogin``)."""

    PHONE_DIGITS = 'phone_digits'
    """Last digits of a masked phone number (``https://funpay.com/security/ipChallenge``)."""

    UNKNOWN = 'unknown'
    """Any other form. Its fields are still read, so it can be answered by field order."""


@dataclass
class SecurityChallengeField(FunPayObject):
    """One input of a security form: an answer slot, in page order."""

    name: str
    """Input ``name`` (``twofactor_code``, ``0``)."""

    label: str
    """Text next to the input: the addon (``Телефон +7***350****``) or the group's label."""

    placeholder: str
    """Input placeholder (``000 000``, ``1234``)."""

    input_type: str
    """Input ``type``, ``text`` when not set."""

    length: int | None
    """How many digits the placeholder promises (``000 000`` is 6), ``None`` if none."""


@dataclass
class SecurityChallenge(FunPayObject):
    """
    A page that asks the user to prove who they are before the account opens.

    Read from the page's structure, not from a list of known field names:
    a form nobody has seen still comes back with its fields.
    """

    kind: SecurityChallengeKind
    """Recognized kind, ``SecurityChallengeKind.UNKNOWN`` for every other form."""

    title: str
    """Page ``<h1>``."""

    hint: str
    """Explanation paragraphs above the form, joined by a space."""

    action: str | None
    """Form ``action`` as written. ``None``: the form posts to the address of its own page."""

    fields: tuple[SecurityChallengeField, ...]
    """Answer slots in page order."""

    shape_hash: str
    """
    Hash of the form's STRUCTURE: title, hint wording, action path, field names, types, labels
    and lengths, with digits, ``*`` and ``+`` masked. The same form shown to two users, or on
    two days, has one hash; it is the key for keeping a form that has no parser yet.
    It has nothing to do with request signing.
    """

    @property
    def action_path(self) -> str | None:
        """``action`` without scheme, host and leading slash; ``None`` if there is no action."""
        if not self.action:
            return None
        return urlparse(self.action).path.lstrip('/') or None

    def form_data(self, *answers: str) -> dict[str, str]:
        """
        Maps answers to the fields in page order. Whitespace is removed:
        FunPay refuses ``469 140`` as a wrong code.

        :raises ValueError: if the number of answers differs from the number of fields.
        """
        if len(answers) != len(self.fields):
            message = f'the form has {len(self.fields)} field(s), got {len(answers)} answer(s)'
            raise ValueError(message)
        return {f.name: ''.join(a.split()) for f, a in zip(self.fields, answers)}
