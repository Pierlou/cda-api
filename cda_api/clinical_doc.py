from datetime import datetime
import json
from pathlib import Path
import xmltodict

from cda_api.models import (
    Assigned,
    AssignedParser,
    Code,
    CodeParser,
    EncompassingEncounter,
    EncompassingEncounterParser,
    Entity,
    EntityParser,
    ExtId,
    ExtIdParser,
    Organization,
    OrganizationParser,
    Patient,
    PatientParser,
    ServiceEvent,
    ServiceEventParser,
)
from cda_api.utils import get, parse_time


class ClinicalDocument:
    def __init__(self, raw: dict):
        self._raw: dict = raw
        self.realm_code: str = get(raw, "realmCode.@code")
        self.id: str = get(raw, "id.@root")
        self.set_id: str = get(raw, "setId.@root")
        self.version_number: str = get(raw, "versionNumber.@value")
        self.title: str = get(raw, "title")
        self.effective_time: datetime = parse_time(get(raw, "effectiveTime.@value"))
        self.language_code: str = get(raw, "languageCode.@code")
        self.type_id = ExtId(
            id=get(raw, "typeId.@root"),
            extension=get(raw, "typeId.@extension"),
        )
        self.template_id = ExtIdParser(get(raw, "templateId")).parse()
        self.confidentiality_code = CodeParser(self._raw["confidentialityCode"]).parse()
        self.patient: Patient = PatientParser(self._raw["recordTarget"]["patientRole"]).parse()
        self.author: Assigned = AssignedParser(self._raw["author"]).parse(
            assigned_key="assignedAuthor",
        )
        self.informant: list[Entity] = [
            EntityParser(i["relatedEntity"]).parse()
            for i in self._raw.get("informant", [])
        ]
        self.custodian = OrganizationParser(
            get(self._raw, "custodian.assignedCustodian.representedCustodianOrganization")
        ).parse(
            type_code=self._raw["custodian"].get("@typeCode"),
            class_code=get(self._raw, "custodian.assignedCustodian").get("@classCode"),
        )
        self.legal_authenticator: Assigned = AssignedParser(self._raw["legalAuthenticator"]).parse(
            assigned_key="assignedEntity",
        )
        # self.participant
        self.documentation_of: list[ServiceEvent] = (
            [ServiceEventParser(do["serviceEvent"]).parse()]
            if isinstance((do := self._raw["documentationOf"]), dict)
            else [
                ServiceEventParser(do["serviceEvent"]).parse()
                for do in self._raw["documentationOf"]
            ]
        )
        self.component_of: EncompassingEncounter = EncompassingEncounterParser(
            get(self._raw, "componentOf.encompassingEncounter")
        ).parse()


    @classmethod
    def load(cls, path: str | Path) -> "ClinicalDocument":
        with open(str(path), encoding="utf-8") as f:
            raw = xmltodict.parse(f.read())["ClinicalDocument"]
        return cls(raw)
