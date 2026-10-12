from abc import ABC
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument


class Api(ABC):
    """Convenience routes to relevant info, according to the specified doc type"""

    def __init__(self, document: "ClinicalDocument"):
        self.doc = document

    def iter_entries(self):
        for section in self.doc.component.sections:
            yield from section.entries

    def get_value_from_code(self, code: str, code_type: str, entry_condition: Callable | None):
        for entry in self.iter_entries():
            if entry_condition is not None and not entry_condition(entry):
                continue
            if getattr(entry, code_type) and getattr(entry, f"match_{code_type}")(code):
                return entry.value.cast()
