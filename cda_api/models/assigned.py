from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import Parser, get, parse_time


@dataclass(frozen=True)
class Assigned(Person):
    class_code: str | None
    code: Code | None
    context_control_code: str | None
    id: list[ExtId]
    represented_organization: Organization
    time: datetime | None
    type_code: str | None


class AssignedParser(Parser):
    def parse(self, assigned_key: str, person_key: str = "assignedPerson") -> Assigned:
        assigned = self.raw[assigned_key]
        person = PersonParser(assigned).parse(key=person_key)
        return Assigned(
            class_code=assigned.get("@classCode"),
            code=CodeParser(c).parse() if (c := self.raw.get("code")) else None,
            time=parse_time(t["@value"]) if (t := self.raw.get("time")) else None,
            context_control_code=self.raw.get("@contextControlCode"),
            type_code=self.raw.get("@typeCode"),
            name=person.name,
            address=person.address,
            telecom=person.telecom,
            id=ExtIdParser(assigned["id"]).parse(),
            represented_organization=OrganizationParser(assigned["representedOrganization"]).parse(),
        )
