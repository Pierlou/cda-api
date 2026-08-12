from dataclasses import dataclass

from cda_api.models.assigned import Assigned, AssignedParser
from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.location import Location, LocationParser
from cda_api.utils import Parser, get


@dataclass(frozen=True)
class EncompassingEncounter:
    code: Code | None
    effective_time: EffectiveTime
    id: list[ExtId]
    location: Location
    responsible_party: Assigned | None


class EncompassingEncounterParser(Parser):
    def parse(self) -> EncompassingEncounter:
        return EncompassingEncounter(
            code=CodeParser(self.raw.get("code")).parse(),
            effective_time=EffectiveTimeParser(et).parse() if (et := self.raw.get("effectiveTime")) else None,
            id=ExtIdParser(self.raw.get("id")).parse(),
            location=LocationParser(get(self.raw, "location.healthCareFacility")).parse(),
            responsible_party=AssignedParser(rp).parse(
                assigned_key="assignedEntity",
            ) if (rp := self.raw.get("responsibleParty")) else None,
        )
