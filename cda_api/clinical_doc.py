import json
from datetime import datetime
from pathlib import Path

import xmltodict

from cda_api.models import (
    Assigned,
    AssignedParser,
    Authorization,
    AuthorizationParser,
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
    Recipient,
    RecipientParser,
    ServiceEvent,
    ServiceEventParser,
)
from cda_api.query import Query
from cda_api.utils import ensure_list, get, parse_time


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
        # Patient
        self.patient: Patient = PatientParser(self._raw["recordTarget"]["patientRole"]).parse()
        # Author of the document
        self.authors: list[Assigned] = AssignedParser(self._raw.get("author")).parse(
            assigned_key="assignedAuthor",
            device_key="assignedAuthoringDevice",
        )
        # Patient consent
        self.authorizations: list[Authorization] = AuthorizationParser(self._raw.get("authorization")).parse()
        # Document recipients
        self.recipients: list[Recipient] = RecipientParser(self._raw.get("informationRecipient")).parse()
        # Patient's relatives (family, emergency, trustworthy...)
        self.informants: list[Entity | Assigned] = [
            (
                EntityParser(i["relatedEntity"]).parse()
                if i.get("relatedEntity")
                else AssignedParser(i).parse(
                    assigned_key="assignedEntity",
                )[0]
            )
            for i in ensure_list(self._raw.get("informant") or [])
        ]
        # Entity in charge of document preservation
        self.custodian: Organization = OrganizationParser(
            get(self._raw, "custodian.assignedCustodian.representedCustodianOrganization")
        ).parse(
            type_code=self._raw["custodian"].get("@typeCode"),
            class_code=get(self._raw, "custodian.assignedCustodian").get("@classCode"),
        )
        # Entity in charge of the document
        self.legal_authenticator: Assigned = AssignedParser(
            self._raw.get("legalAuthenticator")
        ).parse(
            assigned_key="assignedEntity",
        )[0]  # [1..1]
        # Persons involved in the document redaction
        self.participants: list[Participant] = ParticipantParser(
            self._raw.get("participant")
        ).parse()
        # Event described in the document
        self.documentation_of: list[ServiceEvent] = [
            ServiceEventParser(do["serviceEvent"]).parse()
            for do in ensure_list(self._raw["documentationOf"])
        ]
        # Parent process of the described event
        self.component_of: EncompassingEncounter = EncompassingEncounterParser(
            get(self._raw, "componentOf.encompassingEncounter")
        ).parse()
        # Document body
        self.component: Body = BodyParser(self._raw["component"]).parse()

        # should always be last
        self.query = Query(self)

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
