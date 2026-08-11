import os

import pytest

from cda_api import ClinicalDocument

files = os.listdir("tests/data/")


@pytest.mark.parametrize(
    "file",
    files,
)
def test_load_files(file: str):
    ClinicalDocument.load("tests/data/" + file)


@pytest.mark.parametrize(
    "file",
    files,
)
def test_no_missing_parse_call(file: str):
    """Checks that no Parser has been left without calling the parse method"""
    cd = ClinicalDocument.load("tests/data/" + file)
    for attr in dir(cd):
        if attr.startswith("_"):
            continue
        assert "cda_api.models" not in str(getattr(cd, attr))
