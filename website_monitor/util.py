import datetime
import re
from urllib.parse import urlparse
import sys
import ctypes

import aiohttp


PRACTICAL_MAX_INT = sys.maxsize // ctypes.sizeof(ctypes.c_void_p)
"""
A practical maximum value for an integer in Python.
It's handy, for instance, to use it when you want to read all the results from a socket.

Value:
* 32bit machine: (2**31 - 1)//4 = 1152921504606846975
* 64bit machine: (2**63 - 1)//8 = 1152921504606846975

See:
https://docs.python.org/2/library/sys.html#sys.maxsize
https://stackoverflow.com/questions/855191/how-big-can-a-python-list-get#comment112727918_15739630
https://stackoverflow.com/a/1406210/341320
"""


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


def validate_regex(regex: str, raise_error: bool = True) -> re.Pattern | None:
    """
    Validate regex string: the regex must be compilable.

    If the regex is valid, return its re.Pattern.
    Else if raise_error is True, raise ValueError.
    """
    try:
        return re.compile(regex)
    except re.error:
        if raise_error:
            raise ValueError(f"Invalid regex (cannot compile it): {regex}")
        else:
            return None


def get_utcnow() -> datetime.datetime:
    """
    Return the current UTC timestamp in seconds.

    Use this method to make sure you are always using a timestamp with same timezone (UTC).
    """
    return datetime.datetime.utcnow()


def get_utcnow_time_difference_seconds(timestamp_start: datetime.datetime) -> float:
    """
    Return the time difference in seconds between the current UTC datetime and the input datetime.
    """
    return (get_utcnow() - timestamp_start).total_seconds()


def is_likely_text_based_body(response: aiohttp.ClientResponse) -> bool:
    """
    Return True if the response's content type is likely to be text-based (e.g. HTML, JSON, XML, etc.).

    Note: this method is not 100% reliable, but good enough for our purposes.
    """
    content_type = response.content_type.lower()
    return (
        response.charset is not None
        or content_type.startswith("text/")
        or content_type.endswith("+xml")
        or content_type.endswith("+json")
        or content_type.endswith("+xhtml")
        or content_type.endswith("+html")
    )


def is_content_length_less_than(response: aiohttp.ClientResponse, length: int, allow_none_content_length: bool) -> bool:
    content_length = response.headers.get("Content-Length")

    if content_length is None:
        return allow_none_content_length
    else:
        return int(content_length) < length
