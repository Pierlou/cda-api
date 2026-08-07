from dataclasses import dataclass

from cda_api.namespaces import HL7_NS
from cda_api.models.address import Address, AddressParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Patient:
    given_name: str | None
    family_name: str | None
    address: Address | None


FIELDS = {
    "given_name": (None, "hl7:patient/hl7:name/hl7:given"),
    "family_name": (None, "hl7:patient/hl7:name/hl7:family"),
    "address": (AddressParser, "hl7:addr"),
}


class PatientParser(Parser):
    def parse(self) -> Patient:
        patientrole = self.find(
            "hl7:recordTarget/"
            "hl7:patientRole",
        )

        kwargs = {
            field: (
                parser(patientrole).parse()
                if parser
                else patientrole.findtext(xpath, namespaces=HL7_NS)
            )
            for field, (parser, xpath) in FIELDS.items()
        }

        return Patient(**kwargs)
