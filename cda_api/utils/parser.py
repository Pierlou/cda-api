from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, raw: dict):
        self.raw = raw

    @abstractmethod
    def parse(self):
        ...
