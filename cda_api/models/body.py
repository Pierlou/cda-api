import logging
import re
from dataclasses import dataclass

import pandas as pd

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.utils import Parser, ensure_list, get


def get_clean_text(field: str | dict | None) -> str | None:
    """Helper for headers and rows"""
    if field is None:
        return None
    text = (
        field
        if isinstance(field, str)
        else field.get("#text") or field.get("content", {}).get("#text")
    )
    if text is None:
        return None
    return re.sub(
        " +",
        " ",
        text.replace("\n", " "),
    )


@dataclass(frozen=True)
class Table:
    headers: list[str] | None
    rows: list[str | None]
    df: pd.DataFrame | None


class TableParser(Parser):
    def parse(self) -> Table:
        thead = self.raw.get("thead")
        if isinstance(thead, dict):
            tr = (
                thead["tr"]
                if isinstance(thead["tr"], dict)
                # TODO: handle multi headers, for now using the last one as headers
                else thead["tr"][-1]
            )
            # TODO: handle colspan for merged heading cells
            th = ensure_list(tr["th"])
            headers = [h if isinstance(h, str) else get_clean_text(h) for h in th]
        else:
            headers = None

        tbody = self.raw.get("tbody")
        rows: list[list[str | None]] = [
            [get_clean_text(cell) for cell in row["td"]] for row in ensure_list(tbody["tr"])
        ]
        if headers is not None and all(len(headers) == len(row) for row in rows):
            df = pd.DataFrame(rows, columns=headers, dtype=str)
        else:
            logging.warning("A table could not be loaded as DataFrame")
            df = None
        return Table(headers=headers, rows=rows, df=df)


@dataclass(frozen=True)
class Section:
    code: Code | None
    class_code: str | None
    id: list[ExtId]
    mood_code: str | None
    template_id: list[ExtId]
    title: str
    text: str | None
    tables: list[Table]
    # entry


class SectionParser(Parser):
    def parse(self) -> Section:
        text = self.raw.get("text", "")
        tables = None
        if isinstance(text, dict):
            if text.get("table"):
                # we have tables to parse!
                tables = ensure_list(text["table"])
                text = None
            else:
                text = text.get("#text")
        return Section(
            template_id=ExtIdParser(self.raw.get("templateId")).parse(),
            code=CodeParser(self.raw.get("code")).parse(),
            class_code=self.raw.get("@classCode"),
            mood_code=self.raw.get("@moodCode"),
            title=self.raw["title"],
            id=ExtIdParser(self.raw.get("id")).parse(),
            text=None if text is None else get_clean_text(text),
            tables=([] if tables is None else [TableParser(t).parse() for t in tables]),
        )


@dataclass(frozen=True)
class Body:
    content: list[Section] | str
    _type: str


class BodyParser(Parser):
    def parse(self) -> Body:
        if self.raw.get("structuredBody"):
            sections = ensure_list(get(self.raw, "structuredBody.component"))
            return Body(
                _type="structured",
                content=[SectionParser(s["section"]).parse() for s in sections],
            )
        elif self.raw.get("nonXMLBody"):
            return Body(
                _type="nonXML",
                content=self.raw["nonXMLBody"]["text"],
            )
        raise NotImplementedError
