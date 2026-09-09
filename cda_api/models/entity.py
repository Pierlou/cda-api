from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Entity(Person):
    class_code: str
    code: Code


class EntityParser(Parser):
    def _parse(self, person_key: str = "relatedPerson") -> Entity:
        if self.raw is None:
            return None
        person = PersonParser(self.raw).parse(key=person_key)
        return Entity(
            address=person.address,
            name=person.name,
            telecom=person.telecom,
            code=CodeParser(self.raw.get("code")).parse(),
            class_code=self.raw["@classCode"],
        )
