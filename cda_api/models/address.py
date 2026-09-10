from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Address:
    city: str | None
    country: str | None
    county: str | None
    house_number: str | None
    postal_code: str | None
    street_name: str | None
    unit_id: str | None
    use: str | None


class AddressParser(Parser):
    # very few cases of self.raw being a list so keeping just Address if possible,
    # but that means checking the type downstream. Maybe we move to list[Address] anyway at some point?
    def _parse(self) -> Address | list[Address]:
        if isinstance(self.raw, dict):
            return Address(
                house_number=self.raw.get("houseNumber"),
                street_name=self.raw.get("streetName"),
                unit_id=self.raw.get("unitId"),
                postal_code=self.raw.get("postalCode"),
                city=self.raw.get("city"),
                country=self.raw.get("country"),
                county=self.raw.get("county"),
                use=self.raw.get("@use"),
            )
        elif isinstance(self.raw, list):
            return [
                Address(
                    house_number=a.get("houseNumber"),
                    street_name=a.get("streetName"),
                    unit_id=a.get("unitId"),
                    postal_code=a.get("postalCode"),
                    city=a.get("city"),
                    country=a.get("country"),
                    county=a.get("county"),
                    use=a.get("@use"),
                )
                for a in self.raw
            ]
        raise NotImplementedError
