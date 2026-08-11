from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.place import Place, PlaceParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Organization(Place):
    class_code: str | None
    id: list[ExtId]
    standard_industry_class_code: Code | None
    telecom: list[Telecom] | None
    type_code: str | None


class OrganizationParser(Parser):
    def parse(self, type_code: str | None = None, class_code: str | None = None) -> Organization:
        place = PlaceParser(self.raw).parse()
        return Organization(
            name=place.name,
            address=place.address,
            telecom=TelecomParser(self.raw["telecom"]).parse() if self.raw.get("telecom") else None,
            id=ExtIdParser(self.raw["id"]).parse(),
            standard_industry_class_code=(
                CodeParser(self.raw["standardIndustryClassCode"]).parse()
                if self.raw.get("standardIndustryClassCode")
                else None
            ),
            type_code=type_code,
            class_code=class_code,
        )
