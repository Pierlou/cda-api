import logging
import re
from dataclasses import dataclass

import pandas as pd

from cda_api.models.assigned import Assigned, AssignedParser
from cda_api.models.code import Code, CodeParser
from cda_api.models.consumable import Consumable, ConsumableParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.entity import Entity, EntityParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.utils import NullObject, Parser, ensure_list, get


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
class DoseQuantity:
    low: str
    high: str
    unit: str


@dataclass(frozen=True)
class Value(Code):
    xsi_type: str | None
    value: str | None
    unit: str | None
    original_text: str | None


@dataclass(frozen=True)
class Entry:
    _type: str | None
    class_code: str | None
    type_code: str | None
    mood_code: str | None
    template_id: list[ExtId]
    id: list[ExtId]
    code: Code | None
    text: str | None
    status_code: Code | None
    effective_time: EffectiveTime
    target_site_code: Code | None
    # approach_site_code: str | None  # never really understandable
    negation_ind: str | None  # TODO: cast to bool?
    consumable: Consumable | None
    dose_quantity: DoseQuantity | None
    expected_use_time: dict | None
    interpretation_code: Code | None
    max_dose_quantity: dict | None  # TODO: make object?
    precondition: str | None
    # priority_code: None  # always nullFlavor in examples
    quantity: str | None
    # rate_quantity: None  # always nullFlavor in examples
    reference: dict | None  # TODO: make object?
    reference_range: str | None
    repeat_number: str | None
    route_code: Code | None
    value: Value | None
    # entry_relationship: derived from Entry itself? the structure is very similar


class EntryParser(Parser):
    def parse(self) -> list[Entry]:
        if self.raw is None:
            return []
        self.ensure_raw_is_list()
        entries = []
        for parent in self.raw:
            type_code = None
            template_id = []
            keys = list(parent.keys())
            if len(keys) <= 3:  # from experience but might as well be a bad guess
                # intermediary key, stored as _type
                _type = keys[-1]  # key seems to always be last after code and id
                type_code = parent.get("@typeCode")
                if parent.get("templateId"):
                    template_id += ExtIdParser(ExtIdParser(parent["templateId"]).parse())
                entry = parent[_type]
            else:
                _type = None
                entry = parent
            value = None
            if entry.get("value"):
                value_code = NullObject()
                if entry["value"].get("@code"):
                    value_code = CodeParser(entry["value"]).parse()
                value = Value(
                    code=value_code.code,
                    code_system=value_code.code_system,
                    code_system_name=value_code.code_system_name,
                    xsi_type=value.get("@xsi:type"),
                    value=value.get("@value"),
                    original_text=value.get("originalText", {}).get("reference", {}).get("@value"),
                )
            entries.append(
                Entry(
                    _type=_type,
                    class_code=entry.get("@classCode"),
                    type_code=type_code,
                    mood_code=entry.get("@moodCode"),
                    template_id=template_id + ExtIdParser(entry.get("templateId")).parse(),
                    id=ExtIdParser(entry.get("id")).parse(),
                    code=CodeParser(entry.get("@code")).parse(),
                    text=(entry.get("text", {}).get("reference") or {}).get("@value"),
                    status_code=CodeParser(entry.get("statusCode")).parse(),
                    effective_time=EffectiveTimeParser(entry.get("effectiveTime")).parse(),
                    target_site_code=CodeParser(
                        entry.get("targetSiteParser")
                    ).parse(),  # TODO: handle originalText and qualifier
                    negation_ind=entry.get("@negationInd"),
                    consumable=ConsumableParser(entry.get("consumable")).parse(),
                    dose_quantity=(
                        DoseQuantity(
                            low=dq.get("low", {}).get("@value"),
                            high=dq.get("high", {}).get("@value"),
                            unit=dq.get("high", {}).get("@unit"),  # assuming low and high have the same unit
                        )
                        if (dq := entry.get("doseQuantity"))
                        else None
                    ),
                    expected_use_time=entry.get("expectedUseTime"),
                    interpretation_code=CodeParser(entry.get("interpretationCode")).parse(),
                    max_dose_quantity=entry.get("maxDoseQuantity"),
                    precondition=entry.get("precondition", {}).get("precondition", {}).get("criterion", {}).get("reference", {}).get("@value"),
                    quantity=entry.get("quantity", {}).get("@value"),
                    reference=entry.get("reference"),
                    reference_range=entry.get("referenceRange", {}).get("observationRange", {}).get("text"),
                    repeat_number=entry.get("repeatNumber", {}).get("@value"),
                    route_code=CodeParser(entry.get("routeCode")).parse(),
                    value=value,
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
    author: list[Assigned]
    informant: list[Entity]


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
            author=[
                AssignedParser(author).parse(
                    assigned_key="assignedAuthor",
                    device_key="assignedAuthoringDevice",
                )
                for author in self.raw.get("author", [])
            ],
            informant=[
                EntityParser(i["relatedEntity"]).parse() for i in self.raw.get("informant", [])
            ],
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
