from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Address:
    city: str
    house_number: int | None
    street_name: str | None
    unit_id: str | None
    postal_code: str | None
    country: str | None
    county: str | None
    use: str | None


class AddressParser(Parser):
    def parse(self) -> Address | None:
        if self.raw.get("@nullFlavor"):
            return None
        return Address(
            house_number=self.raw.get("houseNumber"),
            street_name=self.raw.get("streetName"),
            unit_id=self.raw.get("unitId"),
            postal_code=self.raw.get("postalCode"),
            city=self.raw["city"],
            country=self.raw.get("country"),
            county=self.raw.get("county"),
            use=self.raw.get("@use"),
        )
