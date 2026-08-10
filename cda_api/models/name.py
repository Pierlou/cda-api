from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class QualifiedName:
    text: str
    qualifier: str | None


@dataclass(frozen=True)
class Name:
    family: list[QualifiedName]
    given: list[QualifiedName]
    prefix: str | None
    suffix: str | None


class NameParser(Parser):
    def parse(self) -> list[Name]:
        return Name(
            prefix=self.raw.get("prefix"),
            suffix=self.raw.get("suffix"),
            family=self.family_given_parse(self.raw["family"]),
            given=self.family_given_parse(self.raw["given"]),
        )

    @staticmethod
    def family_given_parse(value: str | list[str | dict[str, str]]):
        if isinstance(value, str):
            return [QualifiedName(qualifier=None, text=value)]
        else:
            return [
                QualifiedName(
                    qualifier=name["@qualifier"],
                    text=name["#text"],
                )
                if isinstance(name, dict)
                else QualifiedName(
                    qualifier=None,
                    text=name,
                )
                for name in value
            ]
        