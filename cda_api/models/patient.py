from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.person import Person, PersonParser
from cda_api.models.place import Place, PlaceParser
from cda_api.utils import Parser, first_or_none


@dataclass(frozen=True)
class Patient(Person):
    administrative_gender_code: Code
    birth_place: Place
    birth_time: date
    class_code: str
    guardian_persons: list[Person]
    id: list[ExtId]

    @property
    def nir(self) -> str | None:
        found = first_or_none([eid for eid in self.id if eid.id == "1.2.250.1.213.1.4.13"])
        return None if found is None else found.extension


class PatientParser(Parser):
    def _parse(self) -> Patient:
        patient = self.raw["patient"]
        person = PersonParser(self.raw).parse(key="patient")[0]
        return Patient(
            class_code=patient["@classCode"],
            id=ExtIdParser(self.raw["id"]).parse(),
            name=person.name,
            address=person.address,
            telecom=person.telecom,
            birth_time=datetime.strptime(
                patient["birthTime"]["@value"],
                "%Y%m%d",
            ).date(),
            birth_place=PlaceParser(patient["birthplace"]["place"]).parse(),
            administrative_gender_code=CodeParser(patient["administrativeGenderCode"]).parse(),
            guardian_persons=PersonParser(patient.get("guardian")).parse(key="guardianPerson"),
        )
