import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime


class Parser(ABC):
    def __init__(self, raw: dict | list[dict] | None):
        self.raw = raw

    def ensure_raw_is_list(self) -> None:
        self.raw = ensure_list(self.raw)

    @abstractmethod
    def parse(self): ...


def parse_time(time_str: str) -> datetime:
    if re.match(r"^\d{14}\+\d{4}$", time_str):
        return datetime.strptime(time_str, "%Y%m%d%H%M%S%z")
    if re.match(r"^\d{14}$", time_str):
        return datetime.strptime(time_str, "%Y%m%d%H%M%S")
    if re.match(r"^\d{12}$", time_str):
        # many cases of no seconds
        return datetime.strptime(time_str + "00", "%Y%m%d%H%M%S")
    if re.match(r"^\d{8}$", time_str):
        return datetime.strptime(time_str, "%Y%m%d")
    # *sometimes* dates are badly formatted, trying to reconstruct
    logging.warning(f"{time_str} is not in the expected format, trying to get by")
    tmp = time_str.split("+")
    if len(tmp) == 2:
        d, tz = tmp
        if len(d) < 14:
            # guessing seconds are missing
            d = d.ljust(14, "0")
        if len(tz) < 4:
            # too short timezone, adding zeros to the left
            tz = tz.rjust(4, "0")
        return datetime.strptime(f"{d}+{tz}", "%Y%m%d%H%M%S%z")
    raise ValueError(f"Could not parse {time_str} as datetime")


def ensure_list(val: list | dict | None) -> list[dict]:
    if val is None:
        return []
    elif isinstance(val, dict):
        return [val]
    return val


def last_key(d: dict) -> str | None:
    if not d:
        return None
    return list(d.keys())[-1]
