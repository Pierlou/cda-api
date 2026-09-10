from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import NullObject, Parser


@dataclass(frozen=True)
class Perfomer(Person):
    code: Code | None
    id: list[ExtId]
    represented_organization: Organization
    template_id: list[ExtId]
    time: EffectiveTime | None
    type_code: str | None


class PerfomerParser(Parser):
    def _parse(self, assigned_key: str, person_key: str = "assignedPerson") -> Perfomer:
        performer = self.raw[assigned_key]
        person = (
            PersonParser(performer).parse(key=person_key)[0]
            if person_key in performer
            else NullObject()
        )
        return Perfomer(
            type_code=self.raw.get("@typeCode"),
            template_id=ExtIdParser(self.raw.get("templateId")).parse(),
            time=EffectiveTimeParser(self.raw.get("time")).parse(),
            code=CodeParser(self.raw.get("code")).parse(),
            name=person.name,
            address=person.address,
            telecom=person.telecom,
            id=ExtIdParser(performer["id"]).parse(),
            represented_organization=OrganizationParser(
                performer["representedOrganization"]
            ).parse(),
        )
