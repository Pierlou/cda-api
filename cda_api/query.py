from typing import TYPE_CHECKING

from cda_api.utils import first_or_none

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument
    from cda_api.models.entity import Entity
    from cda_api.models.body import Value


class Query:
    """Convenience routes to relevant info"""
    def __init__(self, document: "ClinicalDocument"):
        self.doc = document

    def iter_entries(self):
        for section in self.doc.component.content:
            for entry in section.entries:
                yield entry

    @property
    def mother(self) -> "Entity | None":
        return first_or_none([
            i
            for i in self.doc.informant
            if i.code.code == "MTH"
        ])

    @property
    def biological_mother(self) -> "Entity | None":
        return first_or_none([
            i
            for i in self.doc.informant
            if i.code.code == "NMTH"
        ])

    @property
    def father(self) -> "Entity | None":
        return first_or_none([
            i
            for i in self.doc.informant
            if i.code.code == "FTH"
        ])

    @property
    def biological_father(self) -> "Entity | None":
        return first_or_none([
            i
            for i in self.doc.informant
            if i.code.code == "NFTH"
        ])

    @property
    def mother_profession(self) -> "Value | None":


    @property
    def mother_occupation(self) -> "Value | None":
        for entry in self.iter_entries:
            if entry.code == "11345-6" and entry.subject.code in {"NMTH", "MTH"}:
                return entry.value

    @property
    def number_of_children(self):
        ...