import pytest

from cda_api.models.address import Address


@pytest.mark.parametrize(
    "county, postal_code, expected",
    [
        ("63113", "63000", "63"),
        (None, "63000", "63"),
        ("63113", None, "63"),
        ("97101", "97100", "971"),
        (None, "97100", "971"),
        ("97101", None, "971"),
        (None, None, None),
    ],
)
def test_departement(county: str | None, postal_code: str | None, expected: str | None):
    a = Address(
        city="Belleville",
        country="fr",
        county=county,
        house_number="21",
        postal_code=postal_code,
        street_name="rue de la gare",
        unit_id=None,
        use=None,
    )
    assert (a.departement == expected) if expected is not None else (a.departement is None)
