from datetime import datetime
import json
from pathlib import Path
import xmltodict

from cda_api.models import (
    Author,
    AuthorParser,
    Code,
    CodeParser,
    Entity,
    EntityParser,
    ExtId,
    ExtIdParser,
    Patient,
    PatientParser,
)
from cda_api.utils import get


class ClinicalDocument:
    def __init__(self, raw: dict):
        self._raw: dict = raw
        self.realm_code: str = get(raw, "realmCode.@code")
        self.id: str = get(raw, "id.@root")
        self.set_id: str = get(raw, "setId.@root")
        self.version_number: str = get(raw, "versionNumber.@value")
        self.title: str = get(raw, "title")
        self.effective_time: datetime = datetime.strptime(get(raw, "effectiveTime.@value"), "%Y%m%d%H%M%S%z")
        self.language_code: str = get(raw, "languageCode.@code")
        self.type_id = ExtId(
            id=get(raw, "typeId.@root"),
            extension=get(raw, "typeId.@extension"),
        )
        self.template_ids = ExtIdParser(get(raw, "templateId")).parse()
        self.confidentiality_code = CodeParser(self._raw["confidentialityCode"]).parse()
        self.patient: Patient = PatientParser(self._raw["recordTarget"]["patientRole"]).parse()
        self.author: Author = AuthorParser(self._raw["author"]).parse()
        self.informant: list[Entity] = [
            EntityParser(i["relatedEntity"]).parse()
            for i in self._raw.get("informant", [])
        ]


    @classmethod
    def load(cls, path: str | Path) -> "ClinicalDocument":
        with open(str(path), encoding="utf-8") as f:
            raw = xmltodict.parse(f.read())["ClinicalDocument"]
        return cls(raw)
