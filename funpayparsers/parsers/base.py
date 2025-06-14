from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from funpayparsers.types.base import FunPayObject

T = TypeVar('T', bound=FunPayObject)


class FunPayObjectParser(ABC, Generic[T]):
    def __init__(self, raw_source: str):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """
        self.raw_source = raw_source

    @abstractmethod
    def parse(self) -> T:
        raise NotImplementedError()

    async def async_parse(self) -> T:
        return self.parse()
