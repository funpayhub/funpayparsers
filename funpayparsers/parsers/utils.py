__all__ = ('extract_css_url', )

import re


CSS_URL_RE = re.compile(r'url\(([^()]+)\)', re.IGNORECASE)


def extract_css_url(source: str) -> str:
    """
    Extract the URL from a CSS `url()` pattern in the given string.

    This function looks for the pattern `url(...)`
    and returns the content inside the parentheses.

    Note that it does **not** validate whether the extracted content is a valid URL —
    it simply extracts whatever text is inside `url()`.

    Examples:
        >>> extract_css_url('url(https://sfunpay.com/s/avatar/7q/6b/someimg.jpg)')
        'https://sfunpay.com/s/avatar/7q/6b/someimg.jpg'

        >>> extract_css_url('some text url(not url text)')
        'not url text'

        >>> extract_css_url('not a css url') is None
        True

    :param source: The source string potentially containing a CSS `url()` pattern.
    :return: The extracted text inside `url()` if found; otherwise, `None`.
    """
    match = CSS_URL_RE.search(source)
    return match.group(1) if match else None
