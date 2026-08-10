from abc import ABC, abstractmethod
from datetime import datetime


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


def parse_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%Y%m%d%H%M%S%z")