import pytest
from fastchecks.vutil import validate_regex, validated_web_url, validated_pg_conninfo


def test_valvalidated_web_urlidate_web_url():
    fun = validated_web_url

    assert fun("http://example.com") is not None
    assert fun("https://example.com") is not None
    assert fun("HTTPS://example.com") is not None  # scheme is case-insensitive
    assert fun("httPS://example.com") is not None  # scheme is case-insensitive

    with pytest.raises(ValueError):
        assert fun("file://example.com")  # scheme is not web's

    with pytest.raises(ValueError):
        assert fun("ftp://example.com")  # scheme is not web's

    with pytest.raises(ValueError):
        assert fun("wrong://example.com")  # it's just a wrong scheme


def test_validated_postgres_conninfo():
    fun = validated_pg_conninfo

    assert fun("postgres://localhost") is not None
    assert fun("postgres://localhost/dbname") is not None
    assert fun("postgresql://localhost") is not None
    assert fun("postgresql://localhost/dbname") is not None
    assert fun("postgreSQL://localhost") is not None  # scheme is case-insensitive
    assert fun("postgreSQL://localhost/dbname") is not None  # scheme is case-insensitive

    with pytest.raises(ValueError):
        assert fun("http://localhost")  # scheme is not pg's

    with pytest.raises(ValueError):
        assert fun("https://localhost")  # scheme is not pg's

    with pytest.raises(ValueError):
        assert fun("file://localhost")  # scheme is not pg's

    with pytest.raises(ValueError):
        assert fun("ftp://localhost")  # scheme is not pg's

    with pytest.raises(ValueError):
        assert fun("wrong://localhost")  # it's just a wrong scheme


def test_validate_regex():
    assert validate_regex("ok", raise_error=True) is not None

    assert validate_regex("*", raise_error=False) is None
    with pytest.raises(ValueError):
        validate_regex("*", raise_error=True)

    #
    # Possible vulnerable regex'ex -- accepted yet google-re2 will handle them properly without ReDOS / catastrophic backtracking
    #

    # See:
    # https://learn.snyk.io/lessons/redos/javascript/
    # https://snyk.io/blog/redos-and-catastrophic-backtracking/
    assert validate_regex("A(B|C+)+D") is not None

    # regex that matches any string and captures it
    assert validate_regex("(.|\r|\n)*") is not None
