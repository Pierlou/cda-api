from dataclasses import dataclass
from datetime import datetime

from cda_api.utils import Parser, parse_time


@dataclass(frozen=True)
class EffectiveTime:
    low: datetime | None
    high: datetime | None
    operator: str | None
    xsi_type: str | None
    value: datetime | None


class EffectiveTimeParser(Parser):
    def parse(self) -> EffectiveTime | None:
        if self.raw is None:
            return None
        operator = None
        if isinstance(self.raw, list):
            if len(self.raw) != 2 or not all(isinstance(_, dict) for _ in self.raw):
                raise NotImplementedError
            operator = self.raw[1].get("operator")
            self.raw: dict = self.raw[0]
        return EffectiveTime(
            low=self.et_parse_time(self.raw.get("low")),
            high=self.et_parse_time(self.raw.get("high")),
            operator=operator,
            xsi_type=self.raw.get("@xsi:type"),
            value=self.et_parse_time(self.raw) if self.raw.get("@value") else None,
        )

    @classmethod
    def et_parse_time(cls, et: dict | None) -> datetime | None:
        if et is None or "@nullFlavor" in et:
            return None
        if "@value" in et:
            return parse_time(et["@value"])
        raise NotImplementedError
