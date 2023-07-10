import pytest
from fastchecks.vutil import validate_regex


def test_validate_regex():
    assert validate_regex("ok", raise_error=True) is not None

    assert validate_regex("*", raise_error=False) is None
    with pytest.raises(ValueError):
        validate_regex("*", raise_error=True)

    # Possible vulnerable regex
    # See:
    # https://learn.snyk.io/lessons/redos/javascript/
    # https://snyk.io/blog/redos-and-catastrophic-backtracking/
    assert validate_regex("A(B|C+)+D") is not None
