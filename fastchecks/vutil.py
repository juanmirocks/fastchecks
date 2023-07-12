#
# Utils for validating data values, specifically user inputs.
# - Further validation functions are defined in the conf module (i.e., those that depend on configuration values).
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

# Note: currently these values are the same as those defined in the postgres DB schema. But they could be smaller, i.e. stricter.
# MAYBE: reuse these values for the schema.
URL_MAX_LEN = 2048
REGEX_MAX_LEN = 2048


def validate_max_len(x: str, max_len: int, varname: str = "string") -> None:
    require(len(x) <= max_len, f"The {varname} cannot have length greater than: {max_len}")


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


def validate_url(
    url: str, accepted_schemes: set[str], raise_error: bool = True, max_len: int = URL_MAX_LEN
) -> ParseResult | None:
    """
    Validate that the given string is a valid URL and has one of the accepted schemes.
    * If the URL is valid, return the urlparse's parsed result.
    * Else:
        * if raise_error is True, raise ValueError.
        * else, return None.
    """
    # See: https://snyk.io/blog/secure-python-url-validation/

    try:
        validate_max_len(url, max_len=max_len, varname="url")
        ret = urlparse(url)
        accept = bool(ret.scheme) and bool(ret.netloc) and ret.scheme in accepted_schemes
    except:
        accept = False

    if accept:
        return ret
    elif raise_error:
        raise ValueError(
            f"Invalid URL (also, it must start with a scheme in {accepted_schemes}, and have max size {max_len}): {url}"
        )
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
        validate_max_len(regex, max_len=REGEX_MAX_LEN, varname="regex")
        return re2.compile(regex)
    except Exception as e:
        if not raise_error:
            return None
        else:
            match e:
                case ValueError():
                    # return early validation error for max_len for expressivity
                    raise
                case _:
                    raise ValueError(
                        f"Invalid regex (cannot compile it with google-re2 regex syntax https://github.com/google/re2/wiki/Syntax): {regex}"
                    )


def validated_regex(regex: str) -> str:
    validate_regex(regex, raise_error=True)
    return regex


def validated_regex_accepting_none(regex: str | None) -> str | None:
    if regex is None:
        return None
    else:
        validate_regex(regex, raise_error=True)
        return regex
