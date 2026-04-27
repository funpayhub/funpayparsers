from __future__ import annotations


__all__ = ('ParsingError',)


class ParsingError(Exception):
    def __init__(self, raw_source: str, *, location: str | None = None):
        self.raw_source = raw_source
        self.location = location

    def formatted_source(self) -> str:
        if len(self.raw_source) <= 500:
            return self.raw_source

        return self.raw_source[:250] + '\n...\n' + self.raw_source[-250:]

    def __str__(self) -> str:
        loc = f' at {self.location}' if self.location else ''
        return f'An error occurred while parsing{loc}\n{self.formatted_source()}'
