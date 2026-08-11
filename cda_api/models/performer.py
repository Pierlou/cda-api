from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Perfomer(Person):
    code: Code | None
    time: EffectiveTime | None
    template_id: list[ExtId] | None
    type_code: str | None
    ids: list[ExtId]
    represented_organization: Organization


class PerfomerParser(Parser):
    def parse(self, assigned_key: str, person_key: str = "assignedPerson") -> Perfomer:
        performer = self.raw[assigned_key]
        person = PersonParser(performer).parse(key=person_key)
        return Perfomer(
            type_code=self.raw.get("@typeCode"),
            template_id=ExtIdParser(ti).parse() if (ti := self.raw.get("templateId")) else None,
            time=EffectiveTimeParser(t).parse() if (t := self.raw.get("time")) else None,
            code=CodeParser(c).parse() if (c := self.raw.get("code")) else None,
            name=person.name,
            address=person.address,
            telecom=person.telecom,
            ids=ExtIdParser(performer["id"]).parse(),
            represented_organization=OrganizationParser(performer["representedOrganization"]).parse(),
        )
