from datetime import datetime
from typing import TYPE_CHECKING

from cda_api.api import Api
from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.body import Subject
    from cda_api.models.entity import Entity


class CSE8(Api):
    """Child health certificate specific endpoints"""

    def __init__(self, document: "ClinicalDocument"):
        super().__init__(document)
        # examination details
        exam = [
            se for se in self.doc.documentation_of if se.class_code == "ACT"
        ][0]  # always only one?
        self.exam_date = exam.effective_time.any_value
        self.exam_med_family_name = exam.performers[
            0
        ].name.any_family  # TODO: what if more than one?
        self.exam_med_given_name = exam.performers[0].name.any_given
        self.exam_place_code = exam.performers[
            0
        ].represented_organization.standard_industry_class_code.display_name
        self.exam_qual = exam.code.display_name
        # correspondant
        corre = first_or_none(
            [
                part
                for part in self.doc.participants
                if part.function_code and part.function_code.code == "CORRE"
            ]
        )
        if corre:
            self.treating_med_family_name = corre.name.any_family
            self.treating_med_given_name = corre.name.any_given
            self.treating_med_qual = corre.code.display_name

        # body fields
        self._mother_birth_date = None
        for attr, code, code_type, entry_condition in [
            ("mother_profession", "ORG-099", "qualifier", lambda e: self._is_mother(e.subject)),
            ("mother_profession", "ORG-099", "qualifier", lambda e: self._is_mother(e.subject)),
            ("mother_occupation", "ORG-075", "qualifier", lambda e: self._is_mother(e.subject)),
            ("mother_studies_level", "82589-3", "qualifier", lambda e: self._is_mother(e.subject)),
            (
                "father_profession",
                "ORG-099",
                "qualifier",
                lambda e: self._is_father(e.subject),
            ),  # what is the second parent is a woman, or there is no second parent?
            ("father_occupation", "ORG-075", "qualifier", lambda e: self._is_father(e.subject)),
            ("father_studies_level", "82589-3", "qualifier", lambda e: self._is_father(e.subject)),
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
            ("nb_children_in_household", "85722-7", "qualifier", None),
            ("mother_gravidity", "11996-6", "code", None),  # nb of pregnancies
            ("mother_parity", "11977-6", "code", None),  # nb of labours
            ("mother_nb_premature", "11637-6", "code", None),
            ("mother_nb_stillborn", "57062-2", "code", None),
            ("mother_nb_deceased_before_28_days", "MED-1184", "code", None),
            ("mother_has_had_caesarean", "O82.9", "code", None),
            ("mother_pregnancy_announcement", "75200-6", "code", None),
            ("mother_weight_before_pregnancy", "8348-5", "code", None),
            ("mother_height_before_pregnancy", "8302-2", "code", None),
            ("mother_preeclampsia", "O14.9", "code", None),
            ("mother_hypertension", "O13", "code", None),
            ("mother_pregnancy_diabetes", "O24.4", "code", None),
            # ("mother_other_pathology", "O24.4", "code", None),  # no clear example
            ("mother_nb_days_hospitalisation", "ORG-077", "code", None),
            ("mother_hospitalisation_reason", "ORG-086", "code", None),
            ("trisomy_screening", "GEN-078", "code", None),
            ("nb_ultrasound_scans", "ORG-079", "code", None),
            ("morphology_ultrasound_scan", "ORG-080", "code", None),
            ("early_prenatal_meeting", "GEN-079", "code", None),
            ("hepatitis_antigen_search", "51659-1", "code", None),
            ("nb_foetus", "55281-0", "code", None),
            ("gestational_age", "11885-1", "code", None),
            ("foetal_presentation", "MED-1248", "code", None),
            ("pre_12h_membranic_breach", "MED-166", "code", None),
            ("labour_start", "73813-8", "code", None),
            ("labour_analgesia", "MED-168", "code", None),
            ("birth_method", "57071-3", "code", None),
            ("caesarean_cause", "MED-600", "code", None),
            ("child_diet", "67704-7", "qualifier", None),
        ]:
            value = self.get_value_from_code(code, code_type, entry_condition)
            if value is not None:
                setattr(self, attr, value)

        newborn_infos = next(
            sec for sec in self.doc.component.sections
            if sec.code.code == "57075-4"
        )
        vital_signs = (
            newborn_infos
            .find_subsection("29545-1")
            .find_subsection("8716-3")
            .entries[0]  # hoping it's always like this
        )
        for component in vital_signs.components:
            match component.code.code:
                case "29463-7":
                    self.child_weight = component.value.cast()
                case "8302-2":
                    self.child_height = component.value.cast()
                case "8287-5":
                    self.cranial_perimeter = component.value.cast()
                case "9272-6":
                    self.apgar_1mn = component.value.cast()
                case "9274-2":
                    self.apgar_5mn = component.value.cast()
                case "9271-8":
                    self.apgar_10mn = component.value.cast()

        first_week_pathologies = newborn_infos.find_subsection("11450-4").entries[0]
        for relat in first_week_pathologies.entry_relationship:
            match relat.value.code:
                case "P22.9":
                    self.respiratory_distress = not relat.negation_ind
                case "MED-276":
                    self.antibiotherapy_more_than_48h = not relat.negation_ind
                case "G96.9":
                    self.neurological_pathology = not relat.negation_ind
                case "73994005":
                    self.surgical_emergency = not relat.negation_ind
                case "GEN-092.01.11":
                    self.other_first_week_pathology = not relat.negation_ind
        



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
