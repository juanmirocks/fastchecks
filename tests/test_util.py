import pytest
from fastchecks.util import replace_url_last_segment, validate_regex


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


def test_replace_url_last_segment():
    fun = replace_url_last_segment
    new_segment = "fastchecks"

    test_cases = [
        # (url, expected_result)
        ("postgresql://localhost/postgres", "postgresql://localhost/fastchecks"),
        ("postgresql://localhost/postgres?sslmode=require", "postgresql://localhost/fastchecks?sslmode=require"),
        (
            "postgresql://username:password@localhost:5432/postgres?sslmode=require",
            "postgresql://username:password@localhost:5432/fastchecks?sslmode=require",
        ),
    ]

    for url, expected_result in test_cases:
        assert fun(url, new_segment) == expected_result
