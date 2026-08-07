from dataclasses import dataclass

from cda_api.namespaces import HL7_NS
from cda_api.utils import Parser


@dataclass(frozen=True)
class Address:
    house_number: int | None
    street_name: str | None
    unit_id: str | None
    postal_code: str | None
    city: str | None
    country: str | None


FIELDS = {
    "house_number": "hl7:houseNumber",
    "street_name": "hl7:streetName",
    "unit_id": "hl7:unitID",
    "postal_code": "hl7:postalCode",
    "city": "hl7:city",
    "country": "hl7:country",
}


class AddressParser(Parser):
    def parse(self) -> Address:
        obj = self.find(
            "hl7:addr",
        )

        kwargs = {
            field: obj.findtext(xpath, namespaces=HL7_NS)
            for field, xpath in FIELDS.items()
        }

        return Address(**kwargs)