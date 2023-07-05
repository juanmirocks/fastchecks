import datetime
import re
import aiohttp
from urllib.parse import urlparse

from website_monitor import conf
from website_monitor.types import CheckResult, WebsiteCheck
from website_monitor.util import get_utcnow, get_utcnow_time_difference_seconds, validate_url


async def check_website(session: aiohttp.ClientSession, check: WebsiteCheck, timeout: float | None = None) -> CheckResult:
    """
    Access (GET) website's URL and return monitoring statistics (e.g. return status, response time, etc.).

    The information to check is encapsulated in the input WebsiteCheck instance.
    It's ASSUMED (but not asserted) that the input WebsiteCheck instance is valid.
    Make sure to have validated the inputs before calling this method (e.g. using WebsiteCheck.create_with_validation()).

    Optionally: if check.regex is defined, we check if the website's text body matches the regex.
    """
    timestamp_start = get_utcnow()

    _timeout = conf.DEFAULT_REQ_TIMEOUT_SECONDS if timeout is None else timeout

    # Note: if the input regex is None, theoretically we could do a HEAD request instead of a GET
    # However, often websites do not support HEAD, so we stick to GET
    response_ftr = session.get(check.url, timeout=_timeout)

    try:
        response = await response_ftr

        (regex_str_opt, match_str_opt) = ((None, None) if check.regex is None
                                          else (check.regex, await search_pattern_whole_text_body(check.regex, response)))

        # Get response time after (optionally) fetching the website's content (i.e., if the input regex is not None)
        response_time = get_utcnow_time_difference_seconds(timestamp_start)

        return CheckResult(url=check.url, timestamp_start=timestamp_start, response_time=response_time, response_status=response.status, regex_opt=regex_str_opt, regex_match_opt=match_str_opt)

    except TimeoutError:
        response_time = get_utcnow_time_difference_seconds(timestamp_start)  # we could use the _timeout value, but we want to be precise
        return CheckResult(url=check.url, timestamp_start=timestamp_start, response_time=_timeout, response_status=None, regex_opt=None, regex_match_opt=None, timeout_error=True)

    finally:
        response_ftr.close()


async def search_pattern_whole_text_body(regex: str, response: aiohttp.ClientResponse) -> str | None:
    """
    Search for a regex pattern in the response's content (assumed to be in most cases HTML).

    WARNING: the whole response's body is read in memory.

    MAYBE (Alternatives):
    * If regex search can limited to a line, we could use use response.content.readline() instead of response.text().
    * The text body searched is raw HTML (in most cases), not the HTML's text. If we want to search the HTML's tex only, we would need an HTML parser.
    """
    content = await response.text()
    match_opt = re.search(regex, content)
    if match_opt is not None:
        return match_opt[0]
    else:
        return None
