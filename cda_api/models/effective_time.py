from dataclasses import dataclass
from datetime import datetime

from cda_api.utils import Parser, parse_time


@dataclass(frozen=True)
class EffectiveTime:
    high: datetime | None
    low: datetime | None


class EffectiveTimeParser(Parser):
    def parse(self) -> EffectiveTime:
        return EffectiveTime(
            low=parse_time(l["@value"]) if (l := self.raw.get("low")) else None,
            high=parse_time(h["@value"]) if (h := self.raw.get("high")) else None,
        )
