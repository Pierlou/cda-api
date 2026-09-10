import logging
import os

import pytest
import requests

from cda_api import ClinicalDocument
from .utils import download


files = os.listdir("tests/data/")
urls: list[str] = [
    url
    for f in requests.get(
        "https://api.github.com/repos/ansforge/"
        "interop-outil-cda-testcontenucda3.0-outil-validation-documents-cda/contents/ExemplesCDA"
    ).json()
    if (url := f["download_url"])
]


@pytest.mark.parametrize(
    "url",
    urls,
)
def test_load__remote_files(url: str):
    name = download(url)
    try:
        ClinicalDocument.load(name)
        breakpoint()
    except Exception as e:
        # known exceptions that we don't want to support, uncomment to see why
        if e.__repr__() == "KeyError('ClinicalDocument')":
            logging.warning(f"Unexpected document layout for {url.split('/')[-1]}")
            return
        if "Could not parse " in e.__repr__():
            logging.warning(f"Bad datetime in {url.split('/')[-1]}: {e}")
            return
        raise
    finally:
        os.remove(name)


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
