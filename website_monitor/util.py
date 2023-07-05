import datetime
import re
from urllib.parse import urlparse


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
