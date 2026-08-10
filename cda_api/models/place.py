from dataclasses import dataclass

from cda_api.models.address import Address, AddressParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Place:
    address: Address | None
    name: str | None


class PlaceParser(Parser):
    def parse(self) -> Place:
        p = Place(
            address=AddressParser(self.raw["addr"]).parse() if self.raw.get("addr") else None,
            name=self.raw.get("name"),
        )
        if p.address is None and p.name is None:
            raise Value("Either 'name' or 'address' of a Place shouldn't be None")
        return p
