from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, raw: dict | list[dict] | None):
        self.raw = raw

    def ensure_raw_is_list(self):
        if self.raw is None:
            self.raw = []
        elif isinstance(self.raw, dict):
            self.raw  =[self.raw]

    @abstractmethod
    def parse(self):
        ...
