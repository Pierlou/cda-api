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
            address=AddressParser(self.raw.get("addr")).parse(),
            name=self.raw.get("name"),
        )
        if p.address is None and p.name is None:
            raise ValueError("Either 'name' or 'address' of a Place shouldn't be None")
        return p
