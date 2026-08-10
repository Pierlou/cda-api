from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Code:
    code: str
    display_name: str
    code_system: str
    code_system_name: str | None = None


class CodeParser(Parser):
    def parse(self) -> Code:
        return Code(
            code=self.raw["@code"],
            display_name=self.raw["@displayName"],
            code_system=self.raw["@codeSystem"],
            code_system_name=self.raw.get("@codeSystemName"),
        )
