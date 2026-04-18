from __future__ import annotations


__all__ = ('ParsingError',)


MAX_STORED_RAW_SOURCE = 4096
"""Hard cap on raw_source length kept on ParsingError instances.

Prevents large HTML pages (and anything embedded in them, e.g. CSRF tokens
from ``app-data``) from being retained on exceptions, piped through log
aggregators, or serialized into tracebacks.
"""


class ParsingError(Exception):
    def __init__(self, raw_source: str, *, location: str | None = None):
        self.location = location
        if len(raw_source) > MAX_STORED_RAW_SOURCE:
            half = MAX_STORED_RAW_SOURCE // 2
            self.raw_source = raw_source[:half] + '\n...[truncated]...\n' + raw_source[-half:]
            self.raw_source_truncated = True
        else:
            self.raw_source = raw_source
            self.raw_source_truncated = False

    def formatted_source(self) -> str:
        if len(self.raw_source) <= 500:
            return self.raw_source

        return self.raw_source[:250] + '\n...\n' + self.raw_source[-250:]

    def __str__(self) -> str:
        loc = f' at {self.location}' if self.location else ''
        return f'An error occurred while parsing{loc}\n{self.formatted_source()}'
