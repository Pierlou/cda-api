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
    def _parse(self, key: str) -> list[Person]:
        # in most cases, there will be only one element, so we'll get it directly to end up with a Person object
        self.ensure_raw_is_list()
        return [
            Person(
                name=NameParser(p[key]["name"]).parse(),
                address=AddressParser(p.get("addr")).parse(),
                telecom=TelecomParser(p.get("telecom")).parse(),
            )
            for p in self.raw
        ]
