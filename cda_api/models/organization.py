from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.place import Place, PlaceParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import NullObject, Parser


@dataclass(frozen=True)
class Organization(Place):
    class_code: str | None
    id: list[ExtId]
    standard_industry_class_code: Code | None
    telecom: list[Telecom] | None
    type_code: str | None


class OrganizationParser(Parser):
    def parse(self, type_code: str | None = None, class_code: str | None = None) -> Organization:
        place = (
            PlaceParser(self.raw).parse()
            if self.raw.get("name") or self.raw.get("addr")
            else NullObject()
        )
        return Organization(
            name=place.name,
            address=place.address,
            telecom=TelecomParser(self.raw["telecom"]).parse() if self.raw.get("telecom") else None,
            id=ExtIdParser(self.raw.get("id")).parse(),
            standard_industry_class_code=CodeParser(self.raw.get("standardIndustryClassCode")).parse(),
            type_code=type_code,
            class_code=class_code,
        )
