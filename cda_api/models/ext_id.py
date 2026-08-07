from dataclasses import dataclass


@dataclass(frozen=True)
class ExtId:
    "Dataclass for ids with potential extension"
    id: str
    extension: str | None = None
