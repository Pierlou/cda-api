from abc import ABC, abstractmethod
from datetime import datetime


class Parser(ABC):
    def __init__(self, raw: dict | list[dict] | None):
        self.raw = raw

    def ensure_raw_is_list(self):
        self.raw = ensure_list(self.raw)

    @abstractmethod
    def parse(self):
        ...


def parse_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%Y%m%d%H%M%S%z")


def ensure_list(val: list | dict | None) -> list[dict]:
    if val is None:
        return []
    elif isinstance(val, dict):
        return [val]
    return val
