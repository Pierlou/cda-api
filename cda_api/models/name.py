from dataclasses import dataclass

from cda_api.utils import Parser, first_or_none


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

    @property
    def usual_family(self) -> str | None:
        return first_or_none([f.text for f in self.family if f.qualifier == "CL"])

    @property
    def usual_given(self) -> str | None:
        return first_or_none([f.text for f in self.given if f.qualifier == "CL"])

    @property
    def any_given(self) -> str | None:
        return (
            self.usual_given
            or first_or_none([f.text for f in self.given])
        )

    @property
    def any_family(self) -> str | None:
        return (
            self.usual_family
            or first_or_none([f.text for f in self.family])
        )


class NameParser(Parser):
    def _parse(self) -> Name:
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
