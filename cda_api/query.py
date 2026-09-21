from datetime import date
from typing import TYPE_CHECKING

from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.body import Subject, Value
    from cda_api.models.entity import Entity


class Query:
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
    def biological_father(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informant if i.code.code == "NFTH"])

    @property
    def mother_profession(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_qualifier("ORG-099"):
                return entry.value

    @property
    def mother_studies_level(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_qualifier("82589-3"):
                return entry.value

    @property
    def mother_occupation(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.match_qualifier("ORG-075"):
                return entry.value

    @property
    def father_profession(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_father(entry.subject) and entry.match_qualifier("ORG-099"):
                return entry.value

    @property
    def father_studies_level(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_father(entry.subject) and entry.match_qualifier("82589-3"):
                return entry.value

    @property
    def father_occupation(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_father(entry.subject) and entry.match_qualifier("ORG-075"):
                return entry.value

    @property
    def mother_alcohol_during_pregnancy(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.code.code == "74013-4":
                return entry.value

    @property
    def mother_tobacco_during_pregnancy(self) -> "Value | None":
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.code.code == "74011-8":
                return entry.value

    @property
    def mother_birth_date(self) -> date | None:
        # for whatever reason, the mother's birth date is in both tobbaco and alcohol
        # consumption entries but not in the informant part
        for entry in self.iter_entries():
            if self._is_mother(entry.subject) and entry.code.code in {"74013-4", "74011-8"}:
                return entry.subject.birth_time

    @property
    def nb_children_in_household(self) -> "Value | None":
        for entry in self.iter_entries():
            if entry.qualifier and entry.qualifier.code == "85722-7":
                return entry.value

    @property
    def child_diet(self) -> "Value | None":
        for entry in self.iter_entries():
            if entry.qualifier and entry.qualifier.code == "67704-7":
                return entry.value

    @property
    def mother_gravidity(self) -> "Value | None":
        # nb of pregnancies
        for entry in self.iter_entries():
            if entry.code and entry.code.code == "11996-6":
                return entry.value

    @property
    def mother_parity(self) -> "Value | None":
        # nb of labours
        for entry in self.iter_entries():
            if entry.code and entry.code.code == "11977-6":
                return entry.value
