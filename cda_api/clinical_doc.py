from pathlib import Path
from lxml import etree

from cda_api.namespaces import HL7_NS
from cda_api.models.patient import Patient, PatientParser


class ClinicalDocument:
    def __init__(self, tree: etree._ElementTree):
        self._tree = tree
        self._root = tree.getroot()

    @classmethod
    def load(cls, path: str | Path) -> "ClinicalDocument":
        tree = etree.parse(str(path))
        return cls(tree)
    
    @property
    def title(self) -> str | None:
        node = self._root.find("hl7:title", namespaces=HL7_NS)
        return node.text if node is not None else None

    @property
    def id(self) -> str | None:
        node = self._root.find("hl7:id", namespaces=HL7_NS)
        if node is None:
            return None
        return node.get("extension") or node.get("root")

    @property
    def patient(self) -> Patient:
        return PatientParser(self._root).parse()
