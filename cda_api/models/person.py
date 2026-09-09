from dataclasses import dataclass

from cda_api.models.address import Address, AddressParser
from cda_api.models.name import Name, NameParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Person:
    address: Address | None
    name: Name
    telecom: list[Telecom]


class PersonParser(Parser):
    def _parse(self, key: str) -> Person | list[Person]:
        # very few cases of self.raw being a list so keeping just Person if possible,
        # but that means checking the type downstream. Maybe we move to list[Person] anyway at some point?
        if isinstance(self.raw, dict):
            return Person(
                name=NameParser(self.raw[key]["name"]).parse(),
                address=AddressParser(self.raw.get("addr")).parse(),
                telecom=TelecomParser(self.raw.get("telecom")).parse(),
            )
        elif isinstance(self.raw, list):
            return [
                Person(
                    name=NameParser(p[key]["name"]).parse(),
                    address=AddressParser(p.get("addr")).parse(),
                    telecom=TelecomParser(p.get("telecom")).parse(),
                )
                for p in self.raw
            ]
        raise NotImplementedError
