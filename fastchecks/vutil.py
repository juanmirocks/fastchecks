#
# Utils for validating data values, specifically user inputs.
#
# Further validation functions are defined conf module (which depend on configuration values).
#

from numbers import Number
from urllib.parse import urlparse
import re2

from fastchecks import meta, require


def validate_in_range(name: str, val: Number, min: Number, max: Number) -> Number:
    """
    Validate that the given value is between the given min and max, and return it if it is, otherwise raise ValueError.
    """
    require(
        min <= val <= max,
        f"{name} must be between min & max: [{min}, {max}]",
    )
    return val


def validate_postgres_conninfo(conninfo: str) -> str:
    prefix = "postgresql://"
    require(
        conninfo.startswith(prefix),
        f"The Postgres conninfo must be of URL form and start with 'postgresql://' (e.g. for a local Postgres database, 'postgresql://localhost:5432/{meta.NAME}')",
    )
    return conninfo


def validate_url(url: str, raise_error: bool = True) -> str | None:
    """
    Validate given string is a valid URL.

    If the URL is valid, return its netloc (e.g. "www.example.com").
    Else if raise_error is True, raise ValueError.
    """
    # See: https://snyk.io/blog/secure-python-url-validation/

    ret: str | None
    try:
        result = urlparse(url)
        ret = result.scheme and result.netloc
    except:
        ret = None

    if ret:
        return ret
    elif raise_error:
        raise ValueError(f"Invalid URL: {url}")
    else:
        # ret could have been (without exception) the empty string (which is also falsy), but we return None to avoid confusions
        return None


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
