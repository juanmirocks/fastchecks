#
# Utils for validating data values, specifically user inputs.
# - Further validation functions are defined conf module (which depend on configuration values).
#
# Conventions:
# * Unless otherwise specified, validators must raise ValueError if the value is invalid.
# * Functions that validate a value and (if valid) return it, are prefixed with "validated_".
# * Functions that validate a value and (if valid) return an optionally computed value, are prefixed with "validate_".
#

from numbers import Number
from urllib.parse import urlparse
import re2

from fastchecks import meta, require


def validated_parsed_is_positive_int(val: str) -> int:
    return validated_is_positive_int(int(val))


def validated_is_positive_int(val: int) -> int:
    require(val > 0, f"Value must be positive: {val}")
    return val


def validated_in_range(name: str, val: Number, min: Number, max: Number) -> Number:
    """
    Validate that the given value is between the given min and max, and return it if it is, otherwise raise ValueError.
    """
    require(
        min <= val <= max,
        f"{name} must be between min & max: [{min}, {max}]",
    )
    return val


def validate_url(url: str, raise_error: bool = True) -> str | None:
    """
    Validate that the given string is a valid URL.
    * If the URL is valid, return its netloc (e.g. "www.example.com").
    * Else:
        * if raise_error is True, raise ValueError.
        * else, return None.
    """
    # See: https://snyk.io/blog/secure-python-url-validation/

    ret: str | None
    try:
        result = urlparse(url)
        ret = result.scheme and result.netloc
    except:
        ret = None

    if ret:
        # this means ret is a non-empty string (a truthy value)
        return ret
    elif raise_error:
        raise ValueError(f"Invalid URL: {url}")
    else:
        # ret could have been (without exception) the empty string (which is also falsy), but we return None to avoid confusions
        return None


def validated_url(url: str) -> str:
    validate_url(url, raise_error=True)
    return url


def starts_with_valid_pg_conninfo_protocol(conninfo: str) -> bool:
    """Return True iff the given conninfo starts with a valid URL Postgres protocol, else False"""
    return conninfo.startswith("postgresql://") or conninfo.startswith("postgres://")


def validated_postgres_conninfo(conninfo: str) -> str:
    require(
        starts_with_valid_pg_conninfo_protocol(conninfo) and bool(validate_url(conninfo, raise_error=False)),
        f"The Postgres conninfo must be of URL form and start with 'postgresql://' (e.g. for a local Postgres database, 'postgresql://localhost:5432/{meta.NAME}')",
    )
    return conninfo


def validate_regex(regex: str, raise_error: bool = True) -> re2._Regexp | None:
    """
    Validate regex string: the regex must be compilable with google's re2 library.

    If the regex is valid, return its re2._Regexp for possible later use.
    Else if raise_error is True, raise ValueError.
    """
    try:
        return re2.compile(regex)
    except re2.error:
        if raise_error:
            raise ValueError(
                f"Invalid regex (cannot compile it with google-re2 regex syntax https://github.com/google/re2/wiki/Syntax): {regex}"
            )
        else:
            return None


def validated_regex(regex: str) -> str:
    validate_regex(regex, raise_error=True)
    return regex


def validated_regex_accepting_none(regex: str | None) -> str | None:
    if regex is None:
        return None
    else:
        validate_regex(regex, raise_error=True)
        return regex
