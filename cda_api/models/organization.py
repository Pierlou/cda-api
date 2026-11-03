from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.place import Place, PlaceParser
from cda_api.models.telecom import Telecoms, TelecomParser
from cda_api.utils import NullObject, Parser


@dataclass(frozen=True, repr=False)
class Organization(Place):
    class_code: str | None
    id: list[ExtId]
    standard_industry_class_code: Code | None
    telecom: Telecoms
    type_code: str | None


class OrganizationParser(Parser):
    def _parse(self, type_code: str | None = None, class_code: str | None = None) -> Organization:
        place = (
            PlaceParser(self.raw).parse()
            if self.raw.get("name") or self.raw.get("addr")
            else NullObject()
        )
        return Organization(
            name=place.name,
            address=place.address,
            telecom=TelecomParser(self.raw.get("telecom")).parse(),
            id=ExtIdParser(self.raw.get("id")).parse(),
            standard_industry_class_code=CodeParser(
                self.raw.get("standardIndustryClassCode")
            ).parse(),
            type_code=type_code,
            class_code=class_code,
        )
