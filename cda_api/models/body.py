import logging
import re
from dataclasses import dataclass

import pandas as pd

from cda_api.models.code import Code, CodeParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.utils import Parser, ensure_list, get


def get_clean_text(field: str | dict | list[dict] | None) -> str | None:
    """Helper for headers and rows"""
    if field is None:
        return None
    if isinstance(field, str):
        text = field
    elif isinstance(field, dict):
        if field.get("#text"):
            text = field["#text"]
        elif field.get("content"):
            if isinstance(field.get("content"), dict):
                text = field.get("content").get("#text")
                if text is None:
                    return None
            elif isinstance(field.get("content"), list):
                text = " ".join([t for f in field.get("content") if (t := get_clean_text(f))])
            else:
                raise NotImplementedError
        else:
            return None
    else:
        raise NotImplementedError
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
class Entry:
    _type: str | None
    class_code: str | None
    mood_code: str | None
    template_id: list[ExtId]
    id: list[ExtId]
    code: Code | None
    text: str | None
    status_code: Code | None
    effective_time: EffectiveTime
    # target_side_code: Code | None
    # entry_relationship


class EntryParser(Parser):
    def parse(self) -> list[Entry]:
        if self.raw is None:
            return []
        self.ensure_raw_is_list()
        entries = []
        for parent in self.raw:
            keys = list(parent.keys())
            if len(keys) == 1:
                # intermediary key, stored as _type
                _type = keys[0]
                entry = parent[_type]
            else:
                _type = None
                entry = parent
            entries.append(
                Entry(
                    _type=_type,
                    class_code=entry.get("@classCode"),
                    mood_code=entry.get("@moodCode"),
                    template_id=ExtIdParser(entry.get("templateId")).parse(),
                    id=ExtIdParser(entry.get("id")).parse(),
                    code=CodeParser(entry.get("@code")).parse(),
                    text=(entry.get("text", {}).get("reference") or {}).get("@value"),
                    status_code=CodeParser(entry.get("statusCode")).parse(),
                    effective_time=EffectiveTimeParser(entry.get("effectiveTime")).parse(),
                )
            )
        return entries


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
    entries: list[Entry]


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
            entries=EntryParser(self.raw.get("entry")).parse(),
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
