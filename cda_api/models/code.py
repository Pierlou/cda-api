from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Code:
    code: str
    display_name: str | None
    code_system: str | None
    code_system_name: str | None


class CodeParser(Parser):
    def parse(self) -> Code | None:
        if self.raw is None:
            return None
        return Code(
            code=self.raw["@code"],
            display_name=self.raw.get("@displayName"),
            code_system=self.raw.get("@codeSystem"),
            code_system_name=self.raw.get("@codeSystemName"),
        )
