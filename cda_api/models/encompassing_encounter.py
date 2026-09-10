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
    responsible_party: list[Assigned]


class EncompassingEncounterParser(Parser):
    def _parse(self) -> EncompassingEncounter:
        return EncompassingEncounter(
            code=CodeParser(self.raw.get("code")).parse(),
            effective_time=EffectiveTimeParser(self.raw.get("effectiveTime")).parse(),
            id=ExtIdParser(self.raw.get("id")).parse(),
            location=LocationParser(get(self.raw, "location.healthCareFacility")).parse(),
            responsible_party=AssignedParser(self.raw.get("responsibleParty")).parse(
                assigned_key="assignedEntity",
            ),
        )
