from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.performer import Perfomer, PerfomerParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class ServiceEvent:
    class_code: str | None
    code: Code | None
    effective_time: EffectiveTime | None
    id: list[ExtId]
    performer: list[Perfomer]


class ServiceEventParser(Parser):
    def _parse(self) -> ServiceEvent:
        return ServiceEvent(
            code=CodeParser(self.raw.get("code")).parse(),
            class_code=self.raw.get("@classCode"),
            effective_time=EffectiveTimeParser(self.raw.get("effectiveTime")).parse(),
            id=ExtIdParser(self.raw.get("id")).parse(),
            performer=PerfomerParser(self.raw.get("performer")).parse(
                assigned_key="assignedEntity",
            ),
        )
