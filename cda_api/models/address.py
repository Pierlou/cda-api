from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Address:
    house_number: int | None
    street_name: str | None
    unit_id: str | None
    postal_code: str | None
    city: str | None
    country: str | None


class AddressParser(Parser):
    def parse(self) -> Address:
        return Address(
            house_number=self.raw["houseNumber"],
            street_name=self.raw["streetName"],
            unit_id=self.raw["houseNumber"],
            postal_code=self.raw["houseNumber"],
            city=self.raw["houseNumber"],
            country=self.raw["houseNumber"],
        )