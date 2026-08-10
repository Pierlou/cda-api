from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.place import Place, PlaceParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Organization(Place):
    ids: list[ExtId]
    telecom: list[Telecom] | None
    standard_industry_class_code: Code | None


class OrganizationParser(Parser):
    def parse(self) -> Organization:
        place = PlaceParser(self.raw).parse()
        return Organization(
            name=place.name,
            address=place.address,
            telecom=TelecomParser(self.raw["telecom"]) if self.raw.get("telecom") else None,
            ids=ExtIdParser(self.raw["id"]).parse(),
            standard_industry_class_code=(
                CodeParser(self.raw["standardIndustryClassCode"])
                if self.raw.get("standardIndustryClassCode")
                else None
            ),
        )
