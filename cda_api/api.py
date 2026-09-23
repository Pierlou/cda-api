from datetime import date
from typing import TYPE_CHECKING

from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.body import Subject, Value
    from cda_api.models.entity import Entity


class Api:
    """Convenience routes to relevant info"""

    def __init__(self, document: "ClinicalDocument"):
        self.doc = document

    def iter_entries(self):
        for section in self.doc.component.content:
            yield from section.entries

    @property
    def mother(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informant if i.code.code == "MTH"])

    @property
    def biological_mother(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informant if i.code.code == "NMTH"])

    @property
    def father(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informant if i.code.code == "FTH"])

    @property
    def biological_father(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informant if i.code.code == "NFTH"])

    @staticmethod
    def _is_mother(subj: "Subject | None") -> bool:
        if subj is None or subj.code is None:
            return False
        return subj.code.code in {"NMTH", "MTH"}

    @staticmethod
    def _is_father(subj: "Subject | None") -> bool:
        if subj is None or subj.code is None:
            return False
        return subj.code.code in {"NFTH", "FTH"}

    @property
    def mother_profession(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_qualifier("ORG-099"):
                return entry.value.display_name

    @property
    def mother_studies_level(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_qualifier("82589-3"):
                return entry.value.display_name

    @property
    def mother_occupation(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_qualifier("ORG-075"):
                return entry.value.display_name

    @property
    def father_profession(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_father(entry.subject) and entry.match_qualifier("ORG-099"):
                return entry.value.display_name

    @property
    def father_studies_level(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_father(entry.subject) and entry.match_qualifier("82589-3"):
                return entry.value.display_name

    @property
    def father_occupation(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_father(entry.subject) and entry.match_qualifier("ORG-075"):
                return entry.value.display_name

    @property
    def mother_alcohol_during_pregnancy(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_code("74013-4"):
                return entry.value.value

    @property
    def mother_tobacco_during_pregnancy(self) -> str | None:
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_code("74011-8"):
                return entry.value.value

    @property
    def mother_birth_date(self) -> date | None:
        # for whatever reason, the mother's birth date is in both tobbaco and alcohol
        # consumption entries but not in the informant part
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.code.code in {"74013-4", "74011-8"}:
                return entry.subject.birth_time

    @property
    def nb_children_in_household(self) -> str | None:
        for entry in self.iter_entries():
            if entry.match_qualifier("85722-7"):
                return int(entry.value.value)

    @property
    def child_diet(self) -> str | None:
        for entry in self.iter_entries():
            if entry.match_qualifier("67704-7"):
                return entry.value.display_name

    @property
    def mother_gravidity(self) -> int | None:
        # nb of pregnancies
        for entry in self.iter_entries():
            if entry.code and entry.match_code("11996-6"):
                return int(entry.value.value)

    @property
    def mother_parity(self) -> str | None:
        # nb of labours
        for entry in self.iter_entries():
            if entry.code and entry.match_code("11977-6"):
                return int(entry.value.value)
