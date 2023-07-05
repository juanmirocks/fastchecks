import datetime
import re
import aiohttp
from urllib.parse import urlparse

from website_monitor import conf
from website_monitor.types import CheckResult


async def check_website(session: aiohttp.ClientSession, url: str, regex_ptr_opt: re.Pattern | None = None, timeout: float = None) -> CheckResult:
    """
    Access (GET) website's URL and return monitoring statistics.

    Optionally: check if the website's content matches the input regex.
    """
    validate_url(url)

    timestamp_start = get_utcnow()

    _timeout = conf.DEFAULT_REQ_TIMEOUT_SECONDS if timeout is None else timeout

    # Note: if the input regex is None, theoretically we could do a HEAD request instead of a GET
    # However, often websites do not support HEAD, so we stick to GET
    response_ftr = session.get(url, timeout=_timeout)

    try:
        response = await response_ftr

        (regex_str_opt, match_str_opt) = ((None, None) if regex_ptr_opt is None
                                          else (regex_ptr_opt.pattern, await search_pattern_whole_text_body(regex_ptr_opt, response)))

        # Get response time after (optionally) fetching the website's content (i.e., if the input regex is not None)
        response_time = get_utcnow_time_difference_seconds(timestamp_start)

        return CheckResult(url=url, timestamp_start=timestamp_start, response_time=response_time, response_status=response.status, regex_opt=regex_str_opt, regex_match_opt=match_str_opt)

    except TimeoutError:
        response_time = get_utcnow_time_difference_seconds(timestamp_start)  # we could use the _timeout value, but we want to be precise
        return CheckResult(url=url, timestamp_start=timestamp_start, response_time=_timeout, response_status=None, regex_opt=None, regex_match_opt=None, timeout_error=True)

    finally:
        response_ftr.close()


async def search_pattern_whole_text_body(regex_ptr: re.Pattern, response: aiohttp.ClientResponse) -> str:
    """
    Search for a regex pattern in the response's content (assumed to be in most cases HTML).

    WARNING: the whole response's body is read in memory.

    MAYBE (Alternatives):
    * If regex search can limited to a line, we could use use response.content.readline() instead of response.text().
    * The text body searched is raw HTML (in most cases), not the HTML's text. If we want to search the HTML's tex only, we would need an HTML parser.
    """
    content = await response.text()
    match_opt = regex_ptr.search(content)
    if match_opt is not None:
        return match_opt[0]
    else:
        return None


def validate_url(url: str, raise_error: bool = True) -> str | None:
    """
    Validate given string is a valid URL.

    If the URL is valid, return its netloc (e.g. "www.example.com").
    Else if raise_error is True, raise ValueError.
    """
    # See: https://snyk.io/blog/secure-python-url-validation/

    ret: str
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
