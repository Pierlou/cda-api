from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.place import Place, PlaceParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Location(Place):
    code: Code
    id: list[ExtId]


class LocationParser(Parser):
    def parse(self, place_key: str = "location") -> Location:
        place = PlaceParser(self.raw[place_key]).parse() if self.raw.get(place_key) else None
        return Location(
            name=None if place is None else place.name,
            address=None if place is None else place.address,
            id=ExtIdParser(self.raw.get("id")).parse(),
            code=CodeParser(self.raw["code"]).parse(),
        )
