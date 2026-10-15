from typing import TYPE_CHECKING

from cda_api.doc_types.cse import CSE

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument


class CSE24(CSE):
    """24-month-old child health certificate specific endpoints"""

    def __init__(self, document: "ClinicalDocument"):
        super().__init__(document)
        self.attributes["child_nir"] = self.doc.patient.nir
        exam = [se for se in self.doc.documentation_of if se.class_code == "ACT"][
            0
        ]
        self.attributes["exam_frame"] = exam.performers[0].represented_organization.standard_industry_class_code.display_name

        for attr, code, code_type, entry_condition in [
            ("child_daycare", "PAT-058", "qualifier", None),
            ("mothers_milk_feeding_duration", "PAT-059", "qualifier", None),
            ("mixed_feeding_duration", "PAT-060", "qualifier", None),
            ("saturnism_risk", "MED-181", "qualifier", None),
            ("tuberculosis_risk", "MED-283", "qualifier", None),
            ("screen_exposure", "MED-1275", "qualifier", None),
        ]:
            self.attributes[attr] = self.get_value_from_code(code, code_type, entry_condition)
        
        self.attributes["child_daycare_mode"] = (
            # only here if daycare
            self.get_value_from_code("PAT-048", "qualifier", None)
            if self.attributes["child_daycare"]
            else None
        )

        medical_history = self.doc.component.find_section("11348-0").entries[0]  # always only one?
        self.attributes["prematurity_inf_33_weeks"] = medical_history.find_entryrelationship("MED-183", "value").happened
        domestic_accidents = medical_history.find_entryrelationship("MED-185", "value")
        self.attributes["any_domestic_accident_aft_month9"] = domestic_accidents.happened
        for attr, code in  [
            ("traumatic_shock", "NF0A.4"),
            ("burn", "NE2Z"),
            ("intoxication", "NE61"),
            ("other_domestic_accident", "GEN-092.01.13"),
        ]:
            self.attributes[attr] = domestic_accidents.find_entryrelationship(code).happened

        vital_signs = self.doc.component.find_section("8716-3").find_entry("85353-1")
        for attr, code in  [
            ("child_weight", "29463-7"),
            ("child_height", "8302-2"),
            ("child_cranial_perimeter", "8287-5"),
            ("child_bmi", "39156-5"),
        ]:
            self.attributes[attr] = vital_signs.find_component(code).value.cast()

        psychomot_dev = self.doc.component.find_section("xx-MCH-PsychoMDev")
        self.attributes["neurodev_disorder"] = psychomot_dev.find_entry("MED-1274").value.cast()
        self.attributes["walking_acquired"] = psychomot_dev.find_entry("MED-200").value.cast()
        self.attributes["walking_age"] = (
            None
            if not self.attributes["walking_acquired"]
            else psychomot_dev.find_entry("MED-201").value.cast()
        )

        self.attributes["vaccine_rotavirus_complete"] = True
        for ent in self.vaccinations.entries:
            if ent.consumable.any_match_code("J07CA06"):
                match ent.find_entryrelationship("30973-2").value.cast():
                    case 1:
                        self.attributes["vaccine_dtpc_dose_1"] = ent.happened
                    case 2:
                        self.attributes["vaccine_dtpc_dose_2"] = ent.happened
                    case 3:
                        self.attributes["vaccine_dtpc_dose_3"] = ent.happened
            if ent.consumable.any_match_code("J07BC01"):
                match ent.find_entryrelationship("30973-2").value.cast():
                    case 1:
                        self.attributes["vaccine_hepB_dose_1"] = ent.happened
                    case 2:
                        self.attributes["vaccine_hepB_dose_2"] = ent.happened
                    case 3:
                        self.attributes["vaccine_hepB_dose_3"] = ent.happened
            if ent.consumable.any_match_code("J07AL"):
                match ent.find_entryrelationship("30973-2").value.cast():
                    case 1:
                        self.attributes["vaccine_pneumoc_dose_1"] = ent.happened
                    case 2:
                        self.attributes["vaccine_pneumoc_dose_2"] = ent.happened
                    case 3:
                        self.attributes["vaccine_pneumoc_dose_3"] = ent.happened
            if ent.consumable.any_match_code("J07AH07"):
                match ent.find_entryrelationship("30973-2").value.cast():
                    case 1:
                        self.attributes["vaccine_meningocC_dose_1"] = ent.happened
                    case 2:
                        self.attributes["vaccine_meningocC_dose_2"] = ent.happened
            if ent.consumable.any_match_code("J07AH08"):
                match ent.find_entryrelationship("30973-2").value.cast():
                    case 1:
                        self.attributes["vaccine_meningocACYW_dose_1"] = ent.happened
                    case 2:
                        self.attributes["vaccine_meningocACYW_dose_2"] = ent.happened
            if ent.consumable.any_match_code("J07AH09"):
                match ent.find_entryrelationship("30973-2").value.cast():
                    case 1:
                        self.attributes["vaccine_meningocB_dose_1"] = ent.happened
                    case 2:
                        self.attributes["vaccine_meningocB_dose_2"] = ent.happened
                    case 3:
                        self.attributes["vaccine_meningocB_dose_3"] = ent.happened
            if ent.consumable.any_match_code("J07BH"):
                # true if all doses have been injected
                self.attributes["vaccine_rotavirus_complete"] = (
                    self.attributes["vaccine_rotavirus_complete"] and ent.happened
                )
            if ent.consumable.any_match_code("J07AN"):
                self.attributes["vaccine_bcg"] = ent.happened
        
        self.attributes["food_allergies"] = (
            self.doc.component.find_section("48765-2").entries[0]
            .find_entryrelationship("414285001")
            .value.cast()
        )

        treatments = self.doc.component.find_section("18610-6")
        self.attributes["vrs_immunisation"] = None
        if treatments is not None:
            vrs_immunisation = next(
                (
                    e
                    for e in treatments.entries
                    if e.code.code == "DRUG" and e.consumable.any_match_code("J06BD")
                ),
                None,
            )
            self.attributes["vrs_immunisation"] = (
                vrs_immunisation.happened if vrs_immunisation else None
            )
