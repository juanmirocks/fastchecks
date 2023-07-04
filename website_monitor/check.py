import datetime
import re
import aiohttp
from typing import NamedTuple
from urllib.parse import urlparse

from website_monitor import conf


class CheckResult(NamedTuple):
    url: str
    timestamp_start: float
    response_time: float
    #
    response_status: int | None
    regex_opt: str | None
    regex_match_opt: str | None
    #
    timeout_error: bool = False


async def check_website(session: aiohttp.ClientSession, url: str, regex_ptr_opt: re.Pattern | None = None, timeout: float = None) -> CheckResult:
    """
    Access (GET) website's URL and return monitoring statistics.

    Optionally: check if the website's content matches the input regex.
    """
    assert is_valid_url(url), f"Invalid URL: {url}"

    timestamp_start = datetime.datetime.now().timestamp()

    _timeout = conf.DEFAULT_REQ_TIMEOUT_SECONDS if timeout is None else timeout

    # Note: if the input regex is None, theoretically we could do a HEAD request instead of a GET
    # However, often websites do not support HEAD, so we stick to GET
    response_ftr = session.get(url, timeout=_timeout)

    try:
        response = await response_ftr

        regex_str_opt, match_str_opt = None, None
        if regex_ptr_opt is not None:
            regex_str_opt = regex_ptr_opt.pattern
            content = await response.text()
            match_opt = regex_ptr_opt.search(content)
            if match_opt is not None:
                match_str_opt = match_opt[0]

        # Get response time after (optionally) fetching the website's content (i.e., if the input regex is not None)
        response_time = datetime.datetime.now().timestamp() - timestamp_start

        return CheckResult(url=url, timestamp_start=timestamp_start, response_time=response_time, response_status=response.status, regex_opt=regex_str_opt, regex_match_opt=match_str_opt)

    except TimeoutError:
        response_time = datetime.datetime.now().timestamp() - timestamp_start  # we could use the _timeout value, but we want to be precise
        return CheckResult(url=url, timestamp_start=timestamp_start, response_time=_timeout, response_status=None, regex_opt=None, regex_match_opt=None, timeout_error=True)

    finally:
        response_ftr.close()


# See: https://snyk.io/blog/secure-python-url-validation/
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return (result.scheme != "") and (result.netloc != "")
    except:
        return False
