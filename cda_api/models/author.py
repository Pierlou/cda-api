from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import Parser, get


@dataclass(frozen=True)
class Author(Person):
    class_code: str | None
    time: datetime
    context_control_code: str | None
    type_code: str | None
    ids: list[ExtId]
    represented_organization: Organization


class AuthorParser(Parser):
    def parse(self) -> Author:
        author = self.raw["assignedAuthor"]
        person = PersonParser(author, "assignedPerson").parse()
        return Author(
            class_code=author.get("@classCode"),
            time=datetime.strptime(get(self.raw, "time.@value"), "%Y%m%d%H%M%S%z"),
            context_control_code=self.raw.get("@contextControlCode"),
            type_code=self.raw.get("@typeCode"),
            name=person.name,
            address=person.address,
            telecom=person.telecom,
            ids=ExtIdParser(author["id"]).parse(),
            represented_organization=OrganizationParser(author["representedOrganization"]).parse(),
        )
