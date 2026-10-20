from typing import TYPE_CHECKING

from cda_api.doc_types.cse import CSE
from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument


class CSE8(CSE):
    """8-day-old child health certificate specific endpoints"""

    def __init__(self, document: "ClinicalDocument"):
        super().__init__(document)
        self.attributes["mother_nir"] = None
        for entry in self.iter_entries():
            if self._is_biological_mother(entry.subject) and entry.subject.nir:
                self.attributes["mother_nir"] = entry.subject.nir
                break

        # child's future treating doctor
        corre = first_or_none(
            [
                part
                for part in self.doc.participants
                if part.function_code and part.function_code.code == "CORRE"
            ]
        )
        self.attributes["treating_doc_name"] = corre.name.display if corre else None
        self.attributes["treating_doc_address"] = corre.address.display if corre else None

        # body fields
        for attr, code, code_type, entry_condition in [
            (
                "mother_studies_level",
                "82589-3",
                "qualifier",
                lambda e: self._is_biological_mother(e.subject),
            ),
            (
                "parent2_studies_level",
                "82589-3",
                "qualifier",
                lambda e: self._is_second_parent(e.subject),
            ),
            (
                "mother_alcohol_during_pregnancy",
                "74013-4",
                "code",
                lambda e: self._is_biological_mother(e.subject),
            ),
            (
                "mother_tobacco_during_pregnancy",
                "74011-8",
                "code",
                lambda e: self._is_biological_mother(e.subject),
            ),
            (
                "mother_other_addictions",
                "GEN-092.01.04",
                "qualifier",
                lambda e: self._is_biological_mother(e.subject),
            ),
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
            ("child_tuberculosis_risk", "MED-283", "qualifier", None),
        ]:
            self.attributes[attr] = self.get_value_from_code(code, code_type, entry_condition)

        prebirth_exams = self.doc.component.find_section("57078-8").find_entry("MED-1354")
        for comp in prebirth_exams.components:
            match comp.code.code:
                case "315115008":
                    self.attributes["trisomy_screening"] = comp.value.cast()
                case "ORG-079":
                    self.attributes["nb_ultrasound_scans"] = comp.value.cast()
                case "ORG-080":
                    self.attributes["morphology_ultrasound_scan"] = comp.value.cast()
                case "GEN-079":
                    self.attributes["early_prenatal_meeting"] = comp.value.cast()
                case "51659-1":
                    self.attributes["hepatitis_antigen_search"] = comp.value.cast()

        labor_delivery = self.doc.component.find_section("57074-7").find_subsection("42545-4")
        for ent in labor_delivery.entries:
            match ent.code.code:
                case "55281-0":
                    self.attributes["nb_foetus"] = ent.value.cast()
                case "11885-1":
                    self.attributes["gestational_age"] = ent.value.cast()
                case "MED-1248":
                    self.attributes["foetal_presentation"] = ent.value.cast()
                case "MED-166":
                    self.attributes["pre_12h_membranic_breach"] = ent.value.cast()
                case "73813-8":
                    self.attributes["labour_start"] = ent.value.cast()
                case "MED-168":
                    self.attributes["labour_analgesia"] = ent.value.cast()
                case "57071-3":
                    self.attributes["birth_method"] = ent.value.cast()
                case "MED-600":
                    self.attributes["caesarean_cause"] = ent.value.cast()

        newborn_infos = self.doc.component.find_section("57075-4")
        vital_signs = (
            newborn_infos.find_subsection("29545-1")
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
                    self.attributes["child_respiratory_distress"] = relat.happened
                case "MED-276":
                    self.attributes["child_antibiotherapy_more_than_48h"] = relat.happened
                case "G96.9":
                    self.attributes["child_neurological_pathology"] = relat.happened
                case "73994005":
                    self.attributes["child_surgical_emergency"] = relat.happened
                case "GEN-092.01.11":
                    self.attributes["child_other_first_week_pathology"] = relat.happened

        gestures_deafness = newborn_infos.find_subsection("29554-3")
        self.attributes["specialized_tech_gestures"] = gestures_deafness.find_entry(
            "MED-174"
        ).happened
        deafness_screening = gestures_deafness.find_entry("MED-1304")
        self.attributes["deafness_screening_done"] = (
            None if deafness_screening is None else deafness_screening.happened
        )
        self.attributes["deafness_screening_result"] = (
            None
            if deafness_screening is None
            else deafness_screening.find_entryrelationship("MED-1305").value.cast()
        )

        treatments = newborn_infos.find_subsection("18610-6")
        vrs_immunisation = next(
            (
                e
                for e in treatments.entries
                if e.code.code == "DRUG" and e.consumable.any_match_code("J06BD08")
            ),
            None,
        )
        self.attributes["vrs_immunisation"] = (
            vrs_immunisation.happened if vrs_immunisation else None
        )
        hepB_immunoglobin = next(
            (
                e
                for e in treatments.entries
                if e.code.code == "DRUG" and e.consumable.any_match_code("J06BB04")
            ),
            None,
        )
        self.attributes["hepB_immunoglobin"] = (
            hepB_immunoglobin.happened if hepB_immunoglobin else None
        )

        transfert = first_or_none(
            [
                sec
                for sec in newborn_infos.subsections
                if sec.code.code == "42545-4" and sec.find_entry("ORG-081")
            ]
        )
        if transfert is not None:
            self.attributes["transfert"] = True
            self.attributes["transfert_type"] = transfert.find_entry("ORG-081").value.cast()
            transfert_infos = transfert.find_entry("80413-8")
            self.attributes["transfert_dest_type"] = (
                None if (q := transfert_infos.qualifier) is None else q.value.display_name
            )
            self.attributes["transfert_dest_service"] = (
                ec.display_name if (ec := transfert_infos.participants[0].entity_code) else None
            )
            self.attributes["transfert_dest_name"] = transfert_infos.participants[0].name.display
        else:
            self.attributes["transfert"] = False
            self.attributes["transfert_type"] = None
            self.attributes["transfert_dest_type"] = None
            self.attributes["transfert_dest_service"] = None
            self.attributes["transfert_dest_name"] = None

        vaccine_tuberculosis = next(
            e for e in self.vaccinations.entries if e.consumable.any_match_code("J07AN")
        )
        self.attributes["vaccine_tuberculosis"] = vaccine_tuberculosis.happened
        vaccine_hepB = next(
            e for e in self.vaccinations.entries if e.consumable.any_match_code("J07BC01")
        )
        self.attributes["vaccine_hepB"] = vaccine_hepB.happened
