from dataclasses import dataclass

from cda_api.utils import Parser


@dataclass(frozen=True)
class ExtId:
    "Dataclass for ids with potential extension"
    id: str
    extension: str | None = None


class ExtIdParser(Parser):
    def parse(self) -> list[ExtId]:
        self.ensure_raw_is_list()
        ext_ids = []
        for eid in self.raw:
            ext_ids.append(
                ExtId(
                    id=eid["@root"],
                    extension=eid.get("@extension"),
                )
            )
        return ext_ids
