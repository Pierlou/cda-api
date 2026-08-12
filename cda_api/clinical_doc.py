import json
from datetime import datetime
from pathlib import Path

import xmltodict

from cda_api.models import (
    Assigned,
    AssignedParser,
    Body,
    BodyParser,
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
    Participant,
    ParticipantParser,
    Patient,
    PatientParser,
    ServiceEvent,
    ServiceEventParser,
)
from cda_api.utils import get, parse_time


class ClinicalDocument:
    def __init__(self, raw: dict, name: str):
        self._raw: dict = raw
        self.name: str = name
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
        self.template_id: list[ExtId] = ExtIdParser(get(raw, "templateId")).parse()
        self.confidentiality_code: Code = CodeParser(self._raw["confidentialityCode"]).parse()
        self.patient: Patient = PatientParser(self._raw["recordTarget"]["patientRole"]).parse()
        self.author: Assigned = AssignedParser(self._raw["author"]).parse(
            assigned_key="assignedAuthor",
            device_key="assignedAuthoringDevice",
        )
        self.informant: list[Entity] = [
            EntityParser(i["relatedEntity"]).parse() for i in self._raw.get("informant", [])
        ]
        self.custodian: Organization = OrganizationParser(
            get(self._raw, "custodian.assignedCustodian.representedCustodianOrganization")
        ).parse(
            type_code=self._raw["custodian"].get("@typeCode"),
            class_code=get(self._raw, "custodian.assignedCustodian").get("@classCode"),
        )
        self.legal_authenticator: Assigned = AssignedParser(self._raw["legalAuthenticator"]).parse(
            assigned_key="assignedEntity",
        )
        self.participant: list[Participant] = ParticipantParser(
            self._raw.get("participant")
        ).parse()
        self.documentation_of: list[ServiceEvent] = (
            [ServiceEventParser(do["serviceEvent"]).parse()]
            if isinstance((do := self._raw["documentationOf"]), dict)
            else [ServiceEventParser(k["serviceEvent"]).parse() for k in do]
        )
        self.component_of: EncompassingEncounter = EncompassingEncounterParser(
            get(self._raw, "componentOf.encompassingEncounter")
        ).parse()
        self.component: Body = BodyParser(self._raw["component"]).parse()

    @classmethod
    def load(cls, path: str | Path) -> "ClinicalDocument":
        with open(str(path), encoding="utf-8") as f:
            raw = xmltodict.parse(f.read())["ClinicalDocument"]
        name = ".".join(str(path).split("/")[-1].split(".")[:-1])
        return cls(raw, name)

    def to_json(self, file_path: str | Path | None = None) -> None:
        file_path = file_path or f"{self.name}.json"
        with open(file_path, "w") as f:
            json.dump(self._raw, f)

    def export(self):
        # TODO: create export from needed keys
        pass
