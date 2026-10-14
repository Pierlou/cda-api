from datetime import datetime
from typing import TYPE_CHECKING

from cda_api.api import Api
from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.body import Subject
    from cda_api.models.entity import Entity


class CSE8(Api):
    """8-days-old child health certificate specific endpoints"""

    def __init__(self, document: "ClinicalDocument"):
        super().__init__(document)
        # examination details
        exam = [
            se for se in self.doc.documentation_of if se.class_code == "ACT"
        ][0]  # always only one?
        self.attributes["exam_date"] = exam.effective_time.any_value
        self.attributes["exam_med_family_name"] = exam.performers[
            0
        ].name.any_family  # TODO: what if more than one?
        self.attributes["exam_med_given_name"] = exam.performers[0].name.any_given
        self.attributes["exam_place_code"] = exam.performers[
            0
        ].represented_organization.standard_industry_class_code.display_name
        self.attributes["exam_qual"] = exam.code.display_name
        # correspondant
        corre = first_or_none(
            [
                part
                for part in self.doc.participants
                if part.function_code and part.function_code.code == "CORRE"
            ]
        )
        if corre:
            self.attributes["treating_med_family_name"] = corre.name.any_family
            self.attributes["treating_med_given_name"] = corre.name.any_given
            self.attributes["treating_med_qual"] = corre.code.display_name

        # body fields
        # for whatever reason, the mother's birth date and NIR are in some of the sections related to her,
        # but not in the informant part
        self.attributes["mother_birth_date"] = None
        self.attributes["mother_nir"] = None
        for entry in self.iter_entries():
            if self._is_natural_mother(entry.subject) and entry.subject.birth_time:
                self.attributes["mother_birth_date"] = entry.subject.birth_time
            if self._is_natural_mother(entry.subject) and entry.subject.nir:
                self.attributes["mother_nir"] = entry.subject.nir
            if self.attributes["mother_birth_date"] and self.attributes["mother_nir"]:
                break
        self.attributes["parent2_link"] = (
            entry.subject.code.code
            if (entry := first_or_none(
                [e for e in self.iter_entries() if self._is_second_parent(e.subject)]
            ))
            else None
        )
        for attr, code, code_type, entry_condition in [
            ("mother_profession", "ORG-099", "qualifier", lambda e: self._is_natural_mother(e.subject)),
            ("mother_profession", "ORG-099", "qualifier", lambda e: self._is_natural_mother(e.subject)),
            ("mother_occupation", "ORG-075", "qualifier", lambda e: self._is_natural_mother(e.subject)),
            ("mother_studies_level", "82589-3", "qualifier", lambda e: self._is_natural_mother(e.subject)),
            (
                "parent2_profession",
                "ORG-099",
                "qualifier",
                lambda e: self._is_second_parent(e.subject),
            ),  # what if there is no second parent?
            ("parent2_occupation", "ORG-075", "qualifier", lambda e: self._is_second_parent(e.subject)),
            ("parent2_studies_level", "82589-3", "qualifier", lambda e: self._is_second_parent(e.subject)),
            (
                "mother_alcohol_during_pregnancy",
                "74013-4",
                "code",
                lambda e: self._is_natural_mother(e.subject),
            ),
            (
                "mother_tobacco_during_pregnancy",
                "74011-8",
                "code",
                lambda e: self._is_natural_mother(e.subject),
            ),
            (
                "mother_other_addictions",
                "GEN-092.01.04",
                "qualifier",
                lambda e: self._is_natural_mother(e.subject),
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
            ("child_tuberculosis_risk", "MED-283", "qualifier", None),
        ]:
            self.attributes[attr] = self.get_value_from_code(code, code_type, entry_condition)

        newborn_infos = self.doc.component.find_section("57075-4")
        vital_signs = (
            newborn_infos
            .find_subsection("29545-1")
            .find_subsection("8716-3")
            .entries[0]  # hoping it's always like this
        )
        for component in vital_signs.components:
            match component.code.code:
                case "29463-7":
                    self.attributes["child_weight"] = component.value.cast()
                case "8302-2":
                    self.attributes["child_height"] = component.value.cast()
                case "8287-5":
                    self.attributes["child_cranial_perimeter"] = component.value.cast()
                case "9272-6":
                    self.attributes["child_apgar_1mn"] = component.value.cast()
                case "9274-2":
                    self.attributes["child_apgar_5mn"] = component.value.cast()
                case "9271-8":
                    self.attributes["child_apgar_10mn"] = component.value.cast()

        first_week_pathologies = newborn_infos.find_subsection("11450-4").entries[0]
        for relat in first_week_pathologies.entry_relationship:
            match relat.value.code:
                case "P22.9":
                    self.attributes["child_respiratory_distress"] = None if relat.negation_ind is None else not relat.negation_ind
                case "MED-276":
                    self.attributes["child_antibiotherapy_more_than_48h"] = None if relat.negation_ind is None else not relat.negation_ind
                case "G96.9":
                    self.attributes["child_neurological_pathology"] = None if relat.negation_ind is None else not relat.negation_ind
                case "73994005":
                    self.attributes["child_surgical_emergency"] = None if relat.negation_ind is None else not relat.negation_ind
                case "GEN-092.01.11":
                    self.attributes["child_other_first_week_pathology"] = None if relat.negation_ind is None else not relat.negation_ind

        gestures_deafness = newborn_infos.find_subsection("29554-3")
        self.attributes["specialized_tech_gestures"] = None if (e := gestures_deafness.find_entry("MED-174")).negation_ind is None else not e.negation_ind
        deafness_screening = gestures_deafness.find_entry("MED-1304")
        self.attributes["deafness_screening_done"] = None if (deafness_screening is None or deafness_screening.negation_ind is None) else not deafness_screening.negation_ind
        self.attributes["deafness_screening_result"] = None if deafness_screening is None else deafness_screening.find_entryrelationship("MED-1305").value.cast()

        treatments = newborn_infos.find_subsection("18610-6")
        vrs_immunisation = next(
            (e for e in treatments.entries
            if e.code.code == "DRUG"
            and e.consumable.any_match_code("J06BD08")),
            None,
        )
        self.attributes["vrs_immunisation"] = not vrs_immunisation.negation_ind if vrs_immunisation else None
        hepB_immunoglobin = next(
            (e for e in treatments.entries
            if e.code.code == "DRUG"
            and e.consumable.any_match_code("J06BB04")),
            None,
        )
        self.attributes["hepB_immunoglobin"] = not hepB_immunoglobin.negation_ind if hepB_immunoglobin else None

        transfert = first_or_none([
            sec for sec in newborn_infos.subsections if sec.code.code == "42545-4" and sec.find_entry("ORG-081")
        ])
        if transfert is not None:
            self.attributes["transfert"] = True
            self.attributes["transfert_type"] = transfert.find_entry("ORG-081").value.cast()
            transfert_infos = transfert.find_entry("80413-8")
            self.attributes["transfert_dest_type"] = None if (q := transfert_infos.qualifier) is None else q.value.display_name
            self.attributes["transfert_dest_service"] = ec.display_name if (ec := transfert_infos.participants[0].entity_code) else None
            self.attributes["transfert_dest_name"] = transfert_infos.participants[0].name.display
        else:
            self.attributes["transfert"] = False
            self.attributes["transfert_type"] = None
            self.attributes["transfert_dest_type"] = None
            self.attributes["transfert_dest_service"] = None
            self.attributes["transfert_dest_name"] = None


        vaccinations = self.doc.component.find_section("11369-6")
        vaccine_tuberculosis = next(
            e for e in vaccinations.entries
            if  e.consumable.any_match_code("J07AN")
        )
        self.attributes["vaccine_tuberculosis"] = not vaccine_tuberculosis.negation_ind
        vaccine_hepB = next(
            e for e in vaccinations.entries
            if  e.consumable.any_match_code("J07BC01")
        )
        self.attributes["vaccine_hepB"] = not vaccine_hepB.negation_ind
        
        healthcare_plan = self.doc.component.find_section("18776-5")
        self.attributes["guidance_other_prof"] = healthcare_plan.find_entry("ORG-194", attr="qualifier") is not None
        self.attributes["guidance_pluridisc_structure"] = healthcare_plan.find_entry("ORG-195", attr="qualifier") is not None
        self.attributes["link_pmi_doctor"] = healthcare_plan.find_entry("ORG-196", attr="qualifier") is not None


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
    def _is_natural_mother(subj: "Subject | None") -> bool:
        if subj is None or subj.code is None:
            return False
        return subj.code.code == "NMTH"

    @staticmethod
    def _is_second_parent(subj: "Subject | None") -> bool:
        # requires 2026.01 at least, otherwise the natural mother can have MTH instead of NMTH
        if subj is None or subj.code is None:
            return False
        return subj.code.code in {"MTH", "NFTH", "FTH"}
