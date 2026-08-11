from dataclasses import dataclass
import logging
import re

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import Parser, ensure_list, get


def get_clean_text(field: dict):
    """Helper for headers and rows"""
    return re.sub(
        " +",
        " ",
        (field.get("#text") or field["content"]["#text"]).replace("\n", " "),
    )


@dataclass(frozen=True)
class Table:
    headers: list[str] | None
    rows: str


class TableParser(Parser):
    def parse(self) -> Table:
        thead = self.raw.get("thead")
        print(thead)
        if isinstance(thead, dict):
            tr = (
                thead["tr"]
                if isinstance(thead["tr"], dict)
                # TODO: handle multi headers, for now using the last one as headers
                else thead["tr"][-1]
            )
            # TODO: handle colspan for merged heading cells
            th = ensure_list(tr["th"])
            headers = [
                h
                if isinstance(h, str)
                else get_clean_text(h)
                for h in th
            ]
        else:
            headers = None
        
        # return Table()


@dataclass(frozen=True)
class Section:
    code: Code
    class_code: str | None
    id: ExtId | None
    mood_code: str | None
    template_id: list[ExtId]
    title: str
    # text
    tables: None
    # entry


class SectionParser(Parser):
    def parse(self) -> Section:
        text = self.raw.get("text", {}) or {}
        if not isinstance(text, dict):
            logging.error(f"Invalid text in section: {text}")
            text = {}
        return Section(
            template_id=ExtIdParser(ti).parse() if (ti := self.raw.get("templateId")) else None,
            code=CodeParser(c).parse() if (c := self.raw.get("code")) else None,
            class_code=self.raw.get("@classCode"),
            mood_code=self.raw.get("@moodCode"),
            title=self.raw["title"],
            id=ExtId(id=i["@root"], extension=i.get("@extension")) if (i := self.raw.get("id")) else None,
            tables=(
                []
                if (t := text.get("table")) is None
                else [TableParser(t).parse()]
                if isinstance(t, dict)
                else [
                    TableParser(k).parse()
                    for k in t
                ]
            ),
       )


@dataclass(frozen=True)
class Body:
    content: list[Section] | str
    _type: str


class BodyParser(Parser):
    def parse(self) -> Body:
        if self.raw.get("structuredBody"):
            return Body(
                _type="structured",
                content=(
                    [SectionParser(c["section"]).parse()]
                    if isinstance((c := get(self.raw, "structuredBody.component")), dict)
                    else [
                        SectionParser(s["section"]).parse()
                        for s in c
                    ]
                )
            )
        elif self.raw.get("nonXMLBody"):
            return Body(
                _type="nonXML",
                content=self.raw["nonXMLBody"]["text"],
            )
        raise NotImplementedError
