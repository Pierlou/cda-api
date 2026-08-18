# cda-api

A python wrapper to easily load and manipulate CDA files.
Tests files (in `tests/data/`) are taken from https://github.com/ansforge/interop-exemples-xdm

## Use
The main object is `ClinicalDocument`, which expects a valid CDA XML file to load:
```python
from cda_api import ClinicalDocument
doc = ClinicalDocument.load("tests/data/CNAM-HR_2021.01.xml")  # doc is an instance of ClinicalDocument

# all endpoints of the XML files are now accessible through attributes
doc.id  # -> 1.2.250.1.213.1.1.1.36.2021.1.1
doc.custodian.name  # -> 'Assurance maladie'
doc.patient.address.street_name  # -> 'Avenue de Breteuil'

# the body of the document is in the component attribute. Its sections are available as a list
doc.component.content[0].title  # -> 'Usage et Responsabilités'

# if possible, the tables of each section are available as a pandas DataFrame, otherwise headers and rows are loaded as lists
doc.component.content[2].tables[0].headers  # -> ['Date de délivrance', 'Libellé du vaccin', 'Valence vaccinale', 'Prescrit par', 'Spécialité du prescripteur', 'Établissement du prescripteur', 'Délivré par']

# it's possible to dump the document as JSON using the `to_json` method
doc.to_json("./converted.json")
```
