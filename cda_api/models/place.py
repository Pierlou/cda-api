from dataclasses import dataclass

from cda_api.models.address import Address, AddressParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Place:
    address: Address
    name: str | None


class PlaceParser(Parser):
    def parse(self) -> Place:
        return Place(
            address=AddressParser(self.raw["addr"]).parse(),
            name=self.raw.get("name"),
        )
