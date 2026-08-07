from abc import ABC, abstractmethod
from lxml import etree

from cda_api.namespaces import HL7_NS


class Parser(ABC):
    def __init__(self, root: etree._Element):
        self.root = root

    def find(self, xpath: str):
        return self.root.find(xpath, namespaces=HL7_NS)

    def findtext(self, xpath: str):
        return self.root.findtext(xpath, namespaces=HL7_NS)

    @abstractmethod
    def parse(self):
        ...
