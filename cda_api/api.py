from datetime import datetime
from typing import TYPE_CHECKING, Callable

from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.body import Subject
    from cda_api.models.entity import Entity


class Api:
    """Convenience routes to relevant info"""

    def __init__(self, document: "ClinicalDocument"):
        self.doc = document
        # examination details
        exam = first_or_none([se for se in self.doc.documentation_of if se.class_code == "ACT"])
        if exam:
            self.exam_date = exam.effective_time.any_value
            self.exam_qual = exam.code.display_name
            self.exam_med_family_name = exam.performers[0].name.any_family  # TODO: what if more than one?
            self.exam_med_given_name = exam.performers[0].name.any_given
            self.exam_place_code = exam.performers[0].represented_organization.standard_industry_class_code.display_name
        # correspondant
        corre = first_or_none([part for part in self.doc.participants if part.function_code.code == "CORRE"])
        if corre:
            self.treating_med_family_name = corre.name.any_family
            self.treating_med_given_name = corre.name.any_given
        
        # body fields
        self._mother_birth_date = None
        for attr, code, code_type, entry_condition in [
            ("nb_children_in_household", "85722-7", "qualifier", None),
            ("child_diet", "67704-7", "qualifier", None),
            ("mother_gravidity", "11996-6", "code", None),  # nb of pregnancies
            ("mother_parity", "11977-6", "code", None),  # nb of labours
            ("mother_premature_babies", "11637-6", "code", None),
            ("mother_profession", "ORG-099", "qualifier", lambda e: self._is_mother(e.subject)),
            ("mother_profession", "ORG-099", "qualifier", lambda e: self._is_mother(e.subject)),
            (
                "mother_alcohol_during_pregnancy",
                "74013-4",
                "code",
                lambda e: self._is_mother(e.subject),
            ),
            (
                "mother_tobacco_during_pregnancy",
                "74011-8",
                "code",
                lambda e: self._is_mother(e.subject),
            ),
            (
                "mother_other_addictions",
                "GEN-092.01.04",
                "qualifier",
                lambda e: self._is_mother(e.subject),
            ),
            (
                "child_diet",
                "67704-7",
                "qualifier",
                lambda e: lambda e: True,
            ),
            ("mother_occupation", "ORG-075", "qualifier", lambda e: self._is_mother(e.subject)),
            ("mother_studies_level", "82589-3", "qualifier", lambda e: self._is_mother(e.subject)),
            ("father_profession", "ORG-099", "qualifier", lambda e: self._is_father(e.subject)),
            ("father_occupation", "ORG-075", "qualifier", lambda e: self._is_father(e.subject)),
            ("father_studies_level", "82589-3", "qualifier", lambda e: self._is_father(e.subject)),
        ]:
            value = self.get_value_from_code(code, code_type, entry_condition)
            if value:
                setattr(self, attr, value)

    def iter_entries(self):
        for section in self.doc.component.sections:
            yield from section.entries

    def get_value_from_code(self, code: str, code_type: str, entry_condition: Callable | None):
        for entry in self.iter_entries():
            if entry_condition is not None and not entry_condition(entry):
                continue
            if getattr(entry, code_type) and getattr(entry, f"match_{code_type}")(code):
                return entry.value.cast()

    @property
    def mother(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informants if i.code.code == "MTH"])

    @property
    def biological_mother(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informants if i.code.code == "NMTH"])

    @property
    def father(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informants if i.code.code == "FTH"])

    @property
    def biological_father(self) -> "Entity | None":
        return first_or_none([i for i in self.doc.informants if i.code.code == "NFTH"])

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
    def mother_birth_date(self) -> datetime | None:
        if self._mother_birth_date is None:
            # for whatever reason, the mother's birth date is in some of the sections related to her,
            # but not in the informant part
            for entry in self.iter_entries():
                if self._is_mother(entry.subject) and entry.subject.birth_time:
                    self._mother_birth_date = entry.subject.birth_time
                    break
        return self._mother_birth_date
