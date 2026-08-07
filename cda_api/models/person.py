from dataclasses import dataclass

@dataclass(frozen=True)
class Person:
    given_name: str | None
    family_name: str | None
