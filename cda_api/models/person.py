from dataclasses import dataclass

from cda_api.models.address import Address, AddressParser
from cda_api.models.name import Name, NameParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Person:
    address: Address | None
    name: Name
    telecom: list[Telecom] | None


class PersonParser(Parser):
    def parse(self, key: str) -> Person:
        return Person(
            name=NameParser(self.raw[key]["name"]).parse(),
            address=AddressParser(self.raw["addr"]).parse() if self.raw.get("addr") else None,
            telecom=TelecomParser(self.raw["telecom"]).parse() if self.raw.get("telecom") else None,
        )
