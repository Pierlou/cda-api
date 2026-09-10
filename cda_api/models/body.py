from numpy.f2py.auxfuncs import issigned_long_longarray
from cda_api.models import participant
import logging
import re
from dataclasses import dataclass
from datetime import date

import pandas as pd

from cda_api.models.address import Address, AddressParser
from cda_api.models.code import Code, CodeParser
from cda_api.models.consumable import Consumable, ConsumableParser
from cda_api.models.effective_time import EffectiveTime, EffectiveTimeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.name import Name, NameParser
from cda_api.models.telecom import Telecom, TelecomParser
from cda_api.utils import NullObject, Parser, ensure_list, get, last_key, parse_time


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
            if isinstance(field.get("content"), str):
                text = field.get("content")
            elif isinstance(field.get("content"), dict):
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
    def _parse(self) -> Table:
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
            [
                # *sometimes* the header is in the body
                get_clean_text(cell) for cell in row.get("td", row.get("th", []))
            ]
            for row in ensure_list(tbody["tr"])
        ]
        if headers is None and len(rows) > 1:
            # this pushes the first row as header, not perfect but not harmful
            headers = rows[0]
            rows = rows[1:]
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
class Qualifier:
    name: Code | None
    value: Code


@dataclass(frozen=True)
class Subject:
    type_code: str | None
    template_id: list[ExtId]
    class_code: str | None
    code: Code
    address: Address | None
    name: Name | None
    telecom: list[Telecom]
    birth_time: date | None


class SubjectParser(Parser):
    def _parse(self) -> Subject | None:
        relsubj = self.raw["relatedSubject"]
        subj = relsubj.get("subject")
        return Subject(
            type_code=self.raw.get("@typeCode"),
            template_id=ExtIdParser(self.raw.get("templateId")).parse(),
            class_code=relsubj.get("@classCode"),
            code=CodeParser(relsubj.get("code")).parse(),
            name=NameParser(subj.get("name")).parse() if subj else None,
            address=AddressParser(self.raw.get("addr")).parse(),
            telecom=TelecomParser(self.raw.get("telecom")).parse(),
            birth_time=parse_time(
                subj["birthTime"]["@value"]
            ) if subj and subj.get("birthTime") else None,
        )


@dataclass(frozen=True)
class Value(Code):
    xsi_type: str | None
    value: str | None
    unit: str | None
    original_text: str | None
    qualifier: list[Qualifier]


@dataclass(frozen=True)
class Criterion:
    code: Code | None
    value: Value


class ValueParser(Parser):
    def _parse(self) -> Value | None:
        value_code = NullObject()
        if self.raw.get("@code"):
            value_code = CodeParser(self.raw).parse()
        return Value(
            code=value_code.code,
            code_system=value_code.code_system,
            code_system_name=value_code.code_system_name,
            xsi_type=self.raw.get("@xsi:type"),
            display_name=value_code.display_name,
            value=self.raw.get("@value"),
            unit=self.raw.get("@unit"),
            original_text=self.raw.get("originalText", {}).get("reference", {}).get("@value"),
            qualifier=[
                Qualifier(
                    CodeParser(q.get("name")).parse(),
                    ValueParser(q["value"]).parse(),
                )
                for q in ensure_list(self.raw.get("qualifier") or [])
            ],
        )


@dataclass(frozen=True)
class Relation:
    type: str  # observation, atc, procedure...
    type_code: str | None
    class_code: str | None
    mood_code: str | None
    template_id: list[ExtId]
    id: list[ExtId]
    code: Code | None
    text: str | None
    status_code: Code | None
    effective_time: EffectiveTime | None
    value: str


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
    precondition: list[Criterion]
    # priority_code: None  # always nullFlavor in examples
    quantity: str | None
    # rate_quantity: None  # always nullFlavor in examples
    reference: dict | None  # TODO: make object?
    reference_range: str | None
    repeat_number: str | None
    route_code: Code | None
    value: Value | None
    component: list[Relation]
    subject: Subject | None
    # participant:
    # entry_relationship: nested Entry (etc.), maybe kept as dict? otherwise Relation with more attrs, or have a subclass for entry to allow recursion


class EntryParser(Parser):
    _default_parsing_value = []

    def _parse(self) -> list[Entry]:
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
                    template_id += ExtIdParser(parent["templateId"]).parse()
                entry = parent[_type]
            else:
                _type = None
                entry = parent
            # try:
            entries.append(
                Entry(
                    _type=_type,
                    class_code=entry.get("@classCode"),
                    type_code=type_code,
                    mood_code=entry.get("@moodCode"),
                    template_id=template_id + ExtIdParser(entry.get("templateId")).parse(),
                    id=ExtIdParser(entry.get("id")).parse(),
                    code=CodeParser(entry.get("@code")).parse(),
                    text=((entry.get("text") or {}).get("reference") or {}).get("@value"),
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
                            unit=dq.get("high", {}).get(
                                "@unit"
                            ),  # assuming low and high have the same unit
                        )
                        if (dq := entry.get("doseQuantity"))
                        else None
                    ),
                    expected_use_time=entry.get("expectedUseTime"),
                    interpretation_code=CodeParser(entry.get("interpretationCode")).parse(),
                    max_dose_quantity=entry.get("maxDoseQuantity"),
                    precondition=[
                        Criterion(
                            code=CodeParser(c.get("code")).parse(),
                            value=ValueParser(c.get("value")).parse(),
                        )
                        for p in ensure_list(entry.get("precondition") or [])
                        if (c := p.get("criterion"))
                    ],
                    # (entry.get("precondition") or {})
                    # .get("criterion", {})
                    # .get("reference", {})
                    # .get("@value"),
                    quantity=entry.get("quantity", {}).get("@value"),
                    reference=entry.get("reference"),
                    reference_range=entry.get("referenceRange", {})
                    .get("observationRange", {})
                    .get("text"),
                    repeat_number=entry.get("repeatNumber", {}).get("@value"),
                    route_code=CodeParser(entry.get("routeCode")).parse(),
                    value=ValueParser(entry.get("value")).parse(),
                    component=[
                        Relation(
                            type=lk,
                            type_code=c.get("@typeCode"),
                            class_code=obs.get("@classCode"),
                            mood_code=obs.get("@moodCode"),
                            template_id=ExtIdParser(obs.get("templateId")).parse(),
                            id=ExtIdParser(obs.get("id")).parse(),
                            code=CodeParser(obs.get("code")).parse(),
                            text=obs.get("text", {}).get("reference", {}).get("@value"),
                            status_code=CodeParser(obs.get("code")).parse(),
                            effective_time=EffectiveTimeParser(obs.get("effectiveTime")).parse(),
                            value=ValueParser(obs.get("value")).parse(),
                        )
                        for c in ensure_list((entry.get("component") or []))
                        if (obs := c.get(lk := last_key(c)))
                    ],
                    subject=SubjectParser(entry.get("subject")).parse(),
                )
            )
            # except Exception as e:
            #     breakpoint()
            #     breakpoint()
        return entries


@dataclass(frozen=True)
class Section:
    code: Code | None
    class_code: str | None
    id: list[ExtId]
    mood_code: str | None
    template_id: list[ExtId]
    title: str | None
    text: str | None
    tables: list[Table]
    entries: list[Entry]
    # author: list[Assigned]  # never seen but mentionned in doc
    # informant: list[Entity]  # never seen but mentionned in doc


class SectionParser(Parser):
    def _parse(self) -> Section:
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
            title=self.raw.get("title"),
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
    def _parse(self) -> Body:
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
