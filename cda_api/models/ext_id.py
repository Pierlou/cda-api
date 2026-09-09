from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class ExtId:
    "Dataclass for ids with potential extension"

    id: str
    extension: str | None


class ExtIdParser(Parser):
    _default_parsing_value = []

    def _parse(self) -> list[ExtId]:
        self.ensure_raw_is_list()
        if self.raw[0].get("@nullFlavor"):
            return self._default_parsing_value
        ext_ids = []
        for eid in self.raw:
            ext_ids.append(
                ExtId(
                    id=eid["@root"],
                    extension=eid.get("@extension"),
                )
            )
        return ext_ids
