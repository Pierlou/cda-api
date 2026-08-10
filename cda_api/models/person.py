from dataclasses import dataclass
from datetime import date, datetime

from cda_api.models.name import Name, NameParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Person:
    name: Name


class PersonParser(Parser):
    def parse(self) -> Person:
        return Person(name=NameParser(self.raw["name"]).parse())
