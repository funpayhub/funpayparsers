__all__ = ("extract_avatars", "extract_url")

import re
from typing import Literal, overload

REG_LINKS = re.compile(
    r"\b((?:https?:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"
    r"(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+"
    r"(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
)

REG_AVATARS = re.compile(
    r"(https://sfunpay\.com/s/avatar/[^\s\"']+\.(?:jpg|jpeg|png|webp|gif)|/img/layout/avatar\.png)",
)

@overload
def extract_url(text: str, single: Literal[True]) -> str | None: ...
@overload
def extract_url(text: str, single: Literal[False]) -> list[str]: ...

def extract_url(text: str, single: bool = True) -> str | None | list[str]:
    """
    >>> extract_url("https://funpay.com have big dick!", single=True)
    'https://funpay.com'
    >>> extract_url("Naebal", single=True) is None
    True

    Extract URL(s) from a given source string.

    :param text: Source string to extract URL(s) from.
    :param single: If True, return only the first extracted URL as a string (or None if none found).
                   If False, return a list of all extracted URLs.
    :return: A single URL as a string or None if no URL was found (when single is True),
             or a list of extracted URLs (possibly empty) when single is False.
    """
    m = REG_LINKS.findall(text)

    if single:
        return m[0] if m else None
    return m


@overload
def extract_avatars(text: str, single: Literal[True]) -> str | None: ...
@overload
def extract_avatars(text: str, single: Literal[False]) -> list[str]: ...

def extract_avatars(text: str, single: bool = True) -> str | None | list[str]:
    """
    >>> extract_avatars('<img src="https://sfunpay.com/s/avatar/ab/cd/abcd1234goida.jpg">')
    'https://sfunpay.com/s/avatar/ab/cd/abcd1234goida.jpg'
    >>> extract_avatars('<img src="/img/layout/avatar.png">')
    '/img/layout/avatar.png'
    >>> extract_avatars('<img src="/img/layout/avatar.png"> some text <img src="https://sfunpay.com/s/avatar/ab/cd/abcd1234goida.jpg">', single=False)
    ['/img/layout/avatar.png', 'https://sfunpay.com/s/avatar/ab/cd/abcd1234goida.jpg']
    >>> extract_avatars('<img src="segodnya-bez-avatarki.jpg">') is None
    True

    Extract avatar URL(s) from a given source string.

    Types:
    - Full avatar links like 'https://sfunpay.com/s/avatar/somebigstring.jpg/jpeg/png'
    - Default avatar path '/img/layout/avatar.png'

    :param text: Source string to extract avatar URL(s) from.
    :param single: If True, return only the first extracted avatar URL (or None if not found).
                   If False, return a list of all extracted avatar URLs.
    :return: A single avatar URL or list of avatar URLs.
    """
    m = REG_AVATARS.findall(text)
    if single:
        return m[0] if m else None
    return m
