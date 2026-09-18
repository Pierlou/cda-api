import pytest

from cda_api.models.name import Name, QualifiedName


@pytest.mark.parametrize(
    "qfd_names, expected",
    [
        (
            [
                QualifiedName(text="Martin", qualifier="BR"),
                QualifiedName(text="Martin Dupond", qualifier="CL"),
            ],
            "Martin",
        ),
        (
            [
                QualifiedName(text="Martin", qualifier="CL"),
            ],
            None,
        ),
    ],
)
def test_usual_family(qfd_names: list[QualifiedName], expected: str | None):
    n = Name(
        family=qfd_names,
        given=[QualifiedName(text="Alice", qualifier="BR")],
        prefix=None,
        suffix=None,
    )
    assert (n.usual_family == expected) if expected is not None else (n.usual_family is None)


@pytest.mark.parametrize(
    "qfd_names, expected",
    [
        (
            [
                QualifiedName(text="Alice", qualifier="BR"),
                QualifiedName(text="Alice Jeanne", qualifier="CL"),
            ],
            "Alice",
        ),
        (
            [
                QualifiedName(text="Alice Jeanne", qualifier="CL"),
            ],
            None,
        ),
    ],
)
def test_usual_given(qfd_names: list[QualifiedName], expected: str | None):
    n = Name(
        family=[QualifiedName(text="Martin", qualifier="BR")],
        given=qfd_names,
        prefix=None,
        suffix=None,
    )
    assert (n.usual_given == expected) if expected is not None else (n.usual_given is None)
