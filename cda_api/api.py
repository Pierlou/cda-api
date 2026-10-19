from abc import ABC
from typing import TYPE_CHECKING, Callable

import pandas as pd

if TYPE_CHECKING:
    from cda_api.clinical_doc import ClinicalDocument


class Api(ABC):
    """Convenience routes to relevant info, according to the specified doc type"""

    def __init__(self, document: "ClinicalDocument"):
        self.doc = document
        self.attributes = {}

    def __repr__(self) -> str:
        display = ""
        for k, v in self.attributes.items():
            display += f"{k}: {v}\n"
        return display

    def iter_entries(self):
        for section in self.doc.component.sections:
            yield from section.entries

    def get_value_from_code(self, code: str, code_type: str, entry_condition: Callable | None):
        for entry in self.iter_entries():
            if entry_condition is not None and not entry_condition(entry):
                continue
            if getattr(entry, code_type) and getattr(entry, f"match_{code_type}")(code):
                return entry.value.cast()

    def to_csv(
        self,
        file_path: str | None = None,
        pandas_kwargs: dict = {"encoding": "utf-8", "index": False, "sep": ";"},
    ):
        """Dumps self.attributes as a single-row csv file"""
        df = pd.DataFrame([self.attributes])
        df.to_csv(file_path or f"{self.__class__.__name__.lower()}.csv", **pandas_kwargs)
