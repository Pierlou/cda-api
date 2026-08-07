from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.address import AddressPar


@dataclass(frozen=True)
class Patient:
    given_name: str | None
    family_name: str | None
    address: Address | None
    birth_time: date | None
    telecom: list


class PatientParser(Parser):
    def parse(self) -> Patient:
        patient = self.raw["recordTarget"]["patientRole"]
        return Patient(
            address=Address(

            )
        )
