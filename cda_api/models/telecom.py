from dataclasses import dataclass

from cda_api.utils import Parser, PrettyPrint, first_or_none


@dataclass(frozen=True, repr=False)
class Telecom(PrettyPrint):
    type: str
    use: str | None
    value: str


class Telecoms:
    def __init__(self, tlcs: list[Telecom]):
        self.tlcs: list[Telecom] = tlcs

    def __repr__(self) -> str:
        return self.tlcs.__repr__()

    def tel(self, use: str | None = None) -> str | None:
        return first_or_none(
            [
                tlc.value
                for tlc in self.tlcs
                if tlc.type == "tel" and (use is None or tlc.use == use)
            ]
        )

    def email(self, use: str | None = None) -> str | None:
        return first_or_none(
            [
                tlc.value
                for tlc in self.tlcs
                if tlc.type == "mailto" and (use is None or tlc.use == use)
            ]
        )


class TelecomParser(Parser):
    _default_parsing_value = Telecoms(tlcs=[])

    def _parse(self) -> Telecoms:
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
        return Telecoms(tlcs=telecoms)
