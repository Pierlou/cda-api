from dataclasses import dataclass

from cda_api.utils import Parser, PrettyPrint


@dataclass(frozen=True, repr=False)
class Telecom(PrettyPrint):
    type: str
    use: str | None
    value: str


class TelecomParser(Parser):
    _default_parsing_value = []

    def _parse(self) -> list[Telecom]:
        self.ensure_raw_is_list()
        telecoms = []
        for tlc in self.raw:
            rtype, value = tlc["@value"].split(":", maxsplit=1)
            telecoms.append(
                Telecom(
                    value=value,
                    type=rtype,
                    use=tlc.get("@use"),
                )
            )
        return telecoms
