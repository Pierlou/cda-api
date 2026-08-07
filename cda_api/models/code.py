from dataclasses import dataclass


@dataclass(frozen=True)
class Code:
    code: str
    display_name: str
    code_system: str
    code_system_name: str | None = None
