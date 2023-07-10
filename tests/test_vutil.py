import pytest
from fastchecks.vutil import validate_regex_get_pattern


def test_validate_regex():
    assert validate_regex_get_pattern("ok", raise_error=True) is not None

    assert validate_regex_get_pattern("*", raise_error=False) is None
    with pytest.raises(ValueError):
        validate_regex_get_pattern("*", raise_error=True)

    # Possible vulnerable regex
    # See:
    # https://learn.snyk.io/lessons/redos/javascript/
    # https://snyk.io/blog/redos-and-catastrophic-backtracking/
    assert validate_regex_get_pattern("A(B|C+)+D") is not None
