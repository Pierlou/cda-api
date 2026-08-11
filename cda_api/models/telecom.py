from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class Telecom:
    type: str
    use: str | None
    value: str


class TelecomParser(Parser):
    def parse(self) -> list[Telecom]:
        if isinstance(self.raw, dict) and self.raw.get("@nullFlavor"):
            return []
        self.ensure_raw_is_list()
        telecoms = []
        for tlc in self.raw:
            rtype, value = tlc["@value"].split((":"))
            telecoms.append(
                Telecom(
                    value=value,
                    type=rtype.replace("mailto", "email"),
                    use=tlc.get("@use"),
                )
            )
        return telecoms
