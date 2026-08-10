from dataclasses import dataclass
from datetime import datetime

from cda_api.utils import Parser, parse_time


@dataclass(frozen=True)
class EffectiveTime:
    low: datetime
    high: datetime


class EffectiveTimeParser(Parser):
    def parse(self) -> EffectiveTime:
        return EffectiveTime(
            low=parse_time(self.raw["low"]["@value"]),
            high=parse_time(self.raw["high"]["@value"]),
        )
