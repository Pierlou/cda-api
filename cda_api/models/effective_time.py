from dataclasses import dataclass
from datetime import datetime

from cda_api.utils import Parser, parse_time


@dataclass(frozen=True)
class EffectiveTime:
    low: datetime | None
    high: datetime | None


class EffectiveTimeParser(Parser):
    def parse(self) -> EffectiveTime | None:
        if self.raw is None:
            return None
        return EffectiveTime(
            low=parse_time(l["@value"]) if (l := self.raw.get("low")) else None,
            high=parse_time(h["@value"]) if (h := self.raw.get("high")) else None,
        )
