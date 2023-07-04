import datetime
import re
import aiohttp
from typing import NamedTuple
from urllib.parse import urlparse

from website_monitor import conf


class CheckResult(NamedTuple):
    url: str
    timestamp: float
    response_time: float
    response_status: int
    regex_opt: str | None
    regex_match_opt: str | None


async def check_website(session: aiohttp.ClientSession, url: str, regex_ptr_opt: re.Pattern | None = None, timeout: float = None) -> CheckResult:
    """
    Access (GET) website's URL and return monitoring statistics.

    Optionally: check if the website's content matches the input regex.
    """
    assert is_valid_url(url), f"Invalid URL: {url}"

    timestamp_before = datetime.datetime.now().timestamp()

    _timeout = conf.DEFAULT_REQ_TIMEOUT_CLIENT_TIMEOUT if timeout is None else timeout

    # Note: if the input regex is None, theoretically we could do a HEAD request instead of a GET request
    # However, often websites do not support HEAD requests, so we stick to GET requests
    async with session.get(url, timeout=_timeout) as response:
        regex_str_opt, match_str_opt = None, None
        if regex_ptr_opt is not None:
            regex_str_opt = regex_ptr_opt.pattern
            content = await response.text()
            match_opt = regex_ptr_opt.search(content)
            if match_opt is not None:
                match_str_opt = match_opt[0]

        # Get response time after (optionally) fetching the website's content (i.e., if the input regex is not None)
        timestamp_after = datetime.datetime.now().timestamp()
        response_time = timestamp_after - timestamp_before

        return CheckResult(url, timestamp_before, response_time, response.status, regex_str_opt, match_str_opt)


# See: https://snyk.io/blog/secure-python-url-validation/
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return (result.scheme != "") and (result.netloc != "")
    except:
        return False
