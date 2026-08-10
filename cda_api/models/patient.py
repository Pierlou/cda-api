from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.address import Address, AddressParser
from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.place import Place, PlaceParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Patient:
    class_code: str
    ids: list[ExtId]
    #given_name: str | None
    #family_name: str | None
    address: Address | None
    birth_time: date
    birth_place: Place
    telecom: list[Telecom]
    administrative_gender_code: Code


class PatientParser(Parser):
    def parse(self) -> Patient:
        patient = self.raw["patient"]
        return Patient(
            class_code=patient["@classCode"],
            ids=ExtIdParser(self.raw["id"]).parse(),
            address=AddressParser(self.raw["addr"]).parse(),
            telecom=TelecomParser(self.raw["telecom"]).parse(),
            birth_time=datetime.strptime(
                patient["birthTime"]["@value"],
                "%Y%m%d",
            ).date(),
            birth_place=PlaceParser(patient["birthplace"]["place"]).parse(),
            administrative_gender_code=CodeParser(patient["administrativeGenderCode"]).parse(),
        )
