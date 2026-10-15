from dataclasses import dataclass
import logging

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

    @property
    def departement(self) -> str | None:
        commune = self.county or self.postal_code
        if commune:
            return commune[:3] if commune.startswith("97") else commune[:2]
        return None

    @property
    def street_type_name_split(self) -> tuple[str, str] | None:
        """If possible, splits the street name into a standardized street type and the rest"""
        if not self.street_name:
            return None
        first, rest = self.street_name.split(" ", maxsplit=1)
        match first.lower():
            case "rue":
                return ("rue", rest.lower())
            case "avenue":
                return ("ave", rest.lower())
            case "av":
                return ("ave", rest.lower())
            case "boulevard":
                return ("bld", rest.lower())
            case "bd":
                return ("bld", rest.lower())
            case "place":
                return ("pla", rest.lower())
            case _:
                logging.warning(f"Unknown street type: {first}")
                return None

    @property
    def display(self) -> str:
        disp = ""
        if self.house_number:
            disp += f"{self.house_number} "
        if self.unit_id:
            disp += f"({self.unit_id}) "
        if self.street_name:
            disp += f"{self.street_name} "
        if self.city:
            disp += f"{self.city} "
        if self.country:
            disp += f"{self.country} "
        return disp.strip()


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
