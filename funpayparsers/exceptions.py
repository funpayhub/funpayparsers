from __future__ import annotations


__all__ = ('ParsingError',)


class ParsingError(Exception):
    def __init__(self, raw_source: str):
        self.raw_source = raw_source

    def formatted_source(self) -> str:
        if len(self.raw_source) <= 500:
            return self.raw_source

        return self.raw_source[:250] + '\n...\n' + self.raw_source[-250:]

    def __str__(self) -> str:
        return f'An error occurred while parsing\n{self.formatted_source()}'
