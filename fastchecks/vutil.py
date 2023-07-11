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
from urllib.parse import ParseResult, urlparse
import re2

from fastchecks import meta, require


__FALSE = ["false", "f", "0", "no", "n"]
__TRUE = ["true", "t", "1", "yes", "y"]


def validated_parsed_bool_answer(val: str) -> bool:
    val_low = val.lower()
    if val_low in __TRUE:
        return True
    elif val_low in __FALSE:
        return False
    else:
        raise ValueError(f"Could not parse boolean answer value: {val}")


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


ACCEPTED_WEB_URL_SCHEMES = {"http", "https"}


def validate_url(url: str, accepted_schemes: set[str], raise_error: bool = True) -> ParseResult | None:
    """
    Validate that the given string is a valid URL and has one of the accepted schemes.
    * If the URL is valid, return the urlparse's parsed result.
    * Else:
        * if raise_error is True, raise ValueError.
        * else, return None.
    """
    # See: https://snyk.io/blog/secure-python-url-validation/

    try:
        ret = urlparse(url)
        accept: bool = bool(ret.scheme) and bool(ret.netloc) and ret.scheme in accepted_schemes
    except:
        return None

    if accept:
        return ret
    elif raise_error:
        raise ValueError(f"Invalid URL (also it must start with a scheme in: {accepted_schemes}): {url}")
    else:
        return None


def validated_web_url(url: str) -> str:
    validate_url(url, accepted_schemes=ACCEPTED_WEB_URL_SCHEMES, raise_error=True)
    return url


ACCEPTED_PG_CONNINFO_URL_SCHEMES = {"postgres", "postgresql"}


def validated_pg_conninfo(conninfo: str) -> str:
    require(
        validate_url(conninfo, accepted_schemes=ACCEPTED_PG_CONNINFO_URL_SCHEMES, raise_error=False) is not None,
        f"The Postgres conninfo must be of URL form and start with a valid scheme ({ACCEPTED_PG_CONNINFO_URL_SCHEMES}) (e.g. for a local Postgres database, 'postgresql://localhost:5432/{meta.NAME}')",
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
