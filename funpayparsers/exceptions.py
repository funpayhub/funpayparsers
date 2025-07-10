from __future__ import annotations


__all__ = ('ParsingError',)


class ParsingError(Exception):
    def __init__(self, raw_source: str):
        self.raw_source = raw_source

    def __str__(self):
        return f'An error occurred while parsing {self.raw_source}'
