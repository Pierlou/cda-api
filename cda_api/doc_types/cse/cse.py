from typing import TYPE_CHECKING

from cda_api.api import Api
from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.body import Subject
    from cda_api.models.entity import Entity


class CSE(Api):
    """Child health certificate shared specific endpoints"""

    def __init__(self, document: "ClinicalDocument"):
        super().__init__(document)
        self.attributes["child_last_name"] = self.doc.patient.name.any_family
        self.attributes["child_first_name"] = self.doc.patient.name.any_given
        self.attributes["child_birth_date"] = self.doc.patient.birth_time.strftime("%Y-%m-%d")
        self.attributes["child_sex"] = self.doc.patient.administrative_gender_code.code
        self.attributes["birthplace_label"] = self.doc.patient.birth_place.name
        self.attributes["birthplace_house_number"] = (
            self.doc.patient.birth_place.address.house_number
        )
        self.attributes["birthplace_street_type"], self.attributes["birthplace_street_name"] = (
            self.doc.patient.birth_place.address.street_type_name_split
        )
        self.attributes["birthplace_precision"] = self.doc.patient.birth_place.address.unit_id
        self.attributes["birthplace_postal_code"] = self.doc.patient.birth_place.address.postal_code
        self.attributes["birthplace_city_name"] = self.doc.patient.birth_place.address.city
        self.attributes["home_parent_last_name"] = self.doc.patient.guardian_persons[
            0
        ].name.any_family
        self.attributes["home_parent_first_name"] = self.doc.patient.guardian_persons[
            0
        ].name.any_given
        self.attributes["home_phone"] = self.doc.patient.guardian_persons[0].home_phone
        self.attributes["home_house_number"] = self.doc.patient.guardian_persons[
            0
        ].address.house_number
        self.attributes["home_street_type"], self.attributes["home_street_name"] = (
            self.doc.patient.guardian_persons[0].address.street_type_name_split
        )
        self.attributes["home_phone"] = self.doc.patient.guardian_persons[0].home_phone
        self.attributes["home_precision"] = self.doc.patient.guardian_persons[0].address.unit_id
        self.attributes["home_postal_code"] = self.doc.patient.guardian_persons[
            0
        ].address.postal_code
        self.attributes["home_city_name"] = self.doc.patient.guardian_persons[0].address.city
        # missing bis/ter for both

        # mother
        self.attributes["mother_maiden_name"] = (
            self.biological_mother or self.mother
        ).name.any_family  # not good enough
        self.attributes["mother_first_name"] = (
            self.biological_mother or self.mother
        ).name.any_given
        # for whatever reason, the mother's birth date and NIR are in some of the sections related to her,
        # but not in the informant part
        self.attributes["mother_birth_date"] = None
        for entry in self.iter_entries():
            if self._is_biological_mother(entry.subject) and entry.subject.birth_time:
                self.attributes["mother_birth_date"] = entry.subject.birth_time.strftime("%Y-%m-%d")
                break

        # examination details
        exam = [se for se in self.doc.documentation_of if se.class_code == "ACT"][
            0
        ]  # always only one?
        self.attributes["exam_date"] = exam.effective_time.any_value
        self.attributes["exam_doc_name"] = exam.performers[0].name.display
        self.attributes["exam_doc_qual"] = exam.performers[0].code.display_name

        # body fields
        self.attributes["parent2_link"] = (
            entry.subject.code.code
            if (
                entry := first_or_none(
                    [e for e in self.iter_entries() if self._is_second_parent(e.subject)]
                )
            )
            else None
        )
        for attr, code, code_type, entry_condition in [
            (
                "mother_profession",
                "ORG-099",
                "qualifier",
                lambda e: self._is_biological_mother(e.subject),
            ),
            (
                "mother_profession",
                "ORG-099",
                "qualifier",
                lambda e: self._is_biological_mother(e.subject),
            ),
            (
                "mother_occupation",
                "ORG-075",
                "qualifier",
                lambda e: self._is_biological_mother(e.subject),
            ),
            (
                "parent2_profession",
                "ORG-099",
                "qualifier",
                lambda e: self._is_second_parent(e.subject),
            ),  # what if there is no second parent?
            (
                "parent2_occupation",
                "ORG-075",
                "qualifier",
                lambda e: self._is_second_parent(e.subject),
            ),
            ("nb_children_in_household", "85722-7", "qualifier", None),
            ("child_diet", "67704-7", "qualifier", None),
        ]:
            self.attributes[attr] = self.get_value_from_code(code, code_type, entry_condition)

        self.vaccinations = self.doc.component.find_section("11369-6")
        healthcare_plan = self.doc.component.find_section("18776-5")
        self.attributes["guidance_other_prof"] = (
            healthcare_plan.find_entry("ORG-194", attr="qualifier") is not None
        )
        self.attributes["guidance_pluridisc_structure"] = (
            healthcare_plan.find_entry("ORG-195", attr="qualifier") is not None
        )
        self.attributes["link_pmi_doctor"] = (
            healthcare_plan.find_entry("ORG-196", attr="qualifier") is not None
        )

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
    def _is_biological_mother(subj: "Subject | None") -> bool:
        if subj is None or subj.code is None:
            return False
        return subj.code.code == "NMTH"

    @staticmethod
    def _is_second_parent(subj: "Subject | None") -> bool:
        # requires 2026.01 at least, otherwise the biological mother can have MTH instead of NMTH
        if subj is None or subj.code is None:
            return False
        return subj.code.code in {"MTH", "NFTH", "FTH"}
