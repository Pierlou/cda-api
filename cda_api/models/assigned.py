from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import Parser, get, parse_time


@dataclass(frozen=True)
class Assigned(Person):
    class_code: str | None
    time: datetime
    context_control_code: str | None
    type_code: str | None
    ids: list[ExtId]
    represented_organization: Organization


class AssignedParser(Parser):
    def parse(self, assigned_key: str, person_key: str = "assignedPerson") -> Assigned:
        author = self.raw[assigned_key]
        person = PersonParser(author).parse(key=person_key)
        return Assigned(
            class_code=author.get("@classCode"),
            time=parse_time(get(self.raw, "time.@value")),
            context_control_code=self.raw.get("@contextControlCode"),
            type_code=self.raw.get("@typeCode"),
            name=person.name,
            address=person.address,
            telecom=person.telecom,
            ids=ExtIdParser(author["id"]).parse(),
            represented_organization=OrganizationParser(author["representedOrganization"]).parse(),
        )
