from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Code:
    code: str
    display_name: str | None
    code_system: str | None
    code_system_name: str | None


class CodeParser(Parser):
    def _parse(self) -> Code:
        if "@code" not in self.raw:
            # handling *very* rare edge case
            if self.raw.get("translation"):
                self.raw = self.raw["translation"]
            else:
                raise NotImplementedError
        return Code(
            code=self.raw["@code"],
            display_name=self.raw.get("@displayName"),
            code_system=self.raw.get("@codeSystem"),
            code_system_name=self.raw.get("@codeSystemName"),
        )
