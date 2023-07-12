import pytest
from fastchecks.vutil import (
    validated_parsed_bool_answer,
    validate_regex,
    validated_web_url,
    validate_url,
    validated_pg_conninfo,
    URL_MAX_LEN,
    REGEX_MAX_LEN,
)
from tests.tutil import gen_random_str


def test_validated_parsed_bool_answer_basic():
    fun = validated_parsed_bool_answer

    # we also test with diff cases to demonstrate the check is uncased
    assert fun("truE")
    assert not fun("FaLSE")
    with pytest.raises(ValueError):
        fun("This is not booleable")


def test_validated_web_url():
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


def test_validate_url_max_len():
    fun = validate_url

    arbitrary_url_scheme = "arbitrary"

    scheme = f"{arbitrary_url_scheme}://"
    tld = ".com"
    ok_url = f"{scheme}{gen_random_str(URL_MAX_LEN - (len(scheme) + len(tld)))}{tld}"

    assert (
        fun(ok_url, accepted_schemes={arbitrary_url_scheme}, raise_error=True) is not None
    ), f"Length: {len(ok_url)} -- {ok_url}"

    # Length +1
    with pytest.raises(ValueError) as excinfo:
        bad_url = f"{scheme}{gen_random_str(URL_MAX_LEN - (len(scheme) + len(tld)) + 1)}{tld}"
        fun(bad_url, accepted_schemes={arbitrary_url_scheme}, raise_error=True)
    #
    # assert the max_length is indicated in the error message
    assert str(URL_MAX_LEN) in str(excinfo.value)

    # ok_url not so OK, if we limit the length explicitly (-1)
    with pytest.raises(ValueError):
        fun(ok_url, accepted_schemes={arbitrary_url_scheme}, raise_error=True, max_len=URL_MAX_LEN - 1)

    # Same previous test, except without raising error explicitly
    assert (
        fun(ok_url, accepted_schemes={arbitrary_url_scheme}, raise_error=False, max_len=URL_MAX_LEN - 1) is None
    ), f"Length: {len(ok_url)} -- {ok_url}"


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
    fun = validate_regex

    assert fun("ok", raise_error=True) is not None

    assert fun("*", raise_error=False) is None
    with pytest.raises(ValueError):
        fun("*", raise_error=True)

    #
    # Possible vulnerable regex'ex -- accepted yet google-re2 will handle them properly without ReDOS / catastrophic backtracking
    #

    # See:
    # https://learn.snyk.io/lessons/redos/javascript/
    # https://snyk.io/blog/redos-and-catastrophic-backtracking/
    assert fun("A(B|C+)+D") is not None

    # regex that matches any string and captures it
    assert fun("(.|\r|\n)*") is not None


def test_validate_regex_max_len():
    fun = validate_regex

    ok_regex = gen_random_str(REGEX_MAX_LEN)
    assert fun(ok_regex, raise_error=True) is not None

    bad_regex = ok_regex + "a"  # +1 too much
    with pytest.raises(ValueError) as excinfo:
        fun(bad_regex, raise_error=True)
    #
    # assert the max_length is indicated in the error message
    assert str(REGEX_MAX_LEN) in str(excinfo.value)

    # Same previous test, except without raising error explicitly
    fun(bad_regex, raise_error=False) is None, f"{len(bad_regex)}"
