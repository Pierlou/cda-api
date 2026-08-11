from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId
from cda_api.models.performer import Perfomer, PerfomerParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class ServiceEvent:
    code: Code
    class_code: str | None
    effective_time: EffectiveTime | None
    id: ExtId | None
    performer: list[Perfomer]


class ServiceEventParser(Parser):
    def parse(self) -> ServiceEvent:
        return ServiceEvent(
            code=CodeParser(self.raw["code"]).parse(),
            class_code=self.raw.get("@classCode"),
            effective_time=EffectiveTimeParser(et).parse() if (et := self.raw.get("effectiveTime")) else None,
            id=ExtId(id=i["@root"], extension=i["@extension"]) if (i := self.raw.get("id")) else None,
            performer=PerfomerParser(p).parse(
                assigned_key="assignedEntity",
            ) if (p := self.raw.get("performer")) else None,
        )
