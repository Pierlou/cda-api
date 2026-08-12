from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.entity import Entity, EntityParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.utils import NullObject, Parser


@dataclass(frozen=True)
class Participant(Entity):
    type_code: str | None
    function_code: Code | None
    time: EffectiveTime
    scoping_organization: Organization | None


class ParticipantParser(Parser):
    def parse(self) -> list[Participant]:
        if self.raw is None:
            return []
        self.ensure_raw_is_list()
        participants = []
        for p in self.raw:
            if p.get("associatedPerson"):
                entity: Entity = EntityParser(p).parse(person_key="associatedPerson")
                orga: Organization = OrganizationParser(p.get("scopingOrganization")).parse()
            elif p.get("associatedEntity", {}).get("associatedPerson"):
                entity = Entity = EntityParser(p["associatedEntity"]).parse(person_key="associatedPerson")
                orga: Organization = OrganizationParser(p["associatedEntity"].get("scopingOrganization")).parse()
            participants.append(
                Participant(
                    type_code=p.get("@typeCode"),
                    class_code=entity.class_code,
                    code=entity.code,
                    name=entity.name,
                    address=entity.address,
                    telecom=entity.telecom,
                    function_code=CodeParser(p.get("functionCode")).parse(),
                    time=EffectiveTimeParser(p.get("time")).parse(),
                    scoping_organization=orga,
                )
            )
        return participants
