from abc import ABC, abstractmethod


class FunPayObjectParser(ABC):
    def __init__(self, raw_source: str):
        """
        :param raw_source: raw source of an object (HTML / JSON string)
        """
        self.raw_source = raw_source

    @abstractmethod
    def parse(self):
        raise NotImplementedError()

    async def async_parse(self):
        return self.parse()
