import re2
import aiohttp

from fastchecks import conf
from fastchecks.types import CheckResult, WebsiteCheck
from fastchecks.util import (
    get_utcnow,
    get_utcnow_time_difference_seconds,
    is_likely_text_based_body,
    is_content_length_less_than,
)
from fastchecks.log import MAIN_LOGGER as logging


async def check_website(
    session: aiohttp.ClientSession, check: WebsiteCheck, timeout: float | None = None
) -> CheckResult:
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

        regex_match = (
            None
            if (
                # Note: when the response is not OK (<400), we do not check the regex
                not response.ok
                or check.regex is None
            )
            else await search_pattern_whole_text_body(check.regex, response)
        )

        # Get response time after (optionally) fetching the website's content (i.e., if the input regex is not None)
        response_time = get_utcnow_time_difference_seconds(timestamp_start)

        return CheckResult.response(
            check,
            timestamp_start,
            response_time,
            response_status=response.status,
            regex_match=regex_match,
        )

    except Exception as e:
        response_time = get_utcnow_time_difference_seconds(timestamp_start)

        match e:
            case TimeoutError():
                return CheckResult.failure(
                    check,
                    timestamp_start,
                    response_time,
                    timeout_error=True,
                )
            case aiohttp.ClientConnectorError():
                logging.debug(f"{e}")  # nothing major, it can happen

                return CheckResult.failure(
                    check,
                    timestamp_start,
                    response_time,
                    host_error=True,
                )
            case _:
                # unregistered exception, we log it
                logging.warn(f"UNKNOWN EXCEPTION: {e}", exc_info=True)

                return CheckResult.failure(
                    check,
                    timestamp_start,
                    response_time,
                    other_error=True,
                )

    finally:
        response_ftr.close()


async def search_pattern_whole_text_body(regex: str, response: aiohttp.ClientResponse) -> str | bool | None:
    """
    Search for a regex pattern in the response's content (assumed to be in most cases HTML).

    WARNING: the whole response's body is read in memory.

    To alleviate this:
    * we only read the response's body if it's likely to be text based (in particular, not binary) and
    * the response's Content-Length header is None (note: some websites do not report it) or is less than `__ARBITRARY_TOO_BIG_CONTENT_LENGTH`.
    -
    If, according to the rules above, the response's body is not read, we return None. Thus, the regex does not get tested.


    MAYBE (Alternatives):
    * If regex search can limited to a line, we could use use response.content.readline() instead of response.text().
    * The text body searched is raw HTML (in most cases), not the HTML's text. If we want to search the text of the HTML (or other text-based format) only, we would need a corresponding parser.
    """
    if is_likely_text_based_body(response) and is_content_length_less_than(
        response, length=conf.TOO_BIG_CONTENT_LENGTH_KB, allow_none_content_length=True
    ):
        content = await response.text()
        match_opt = re2.search(regex, content)

        if match_opt:
            return match_opt[0]
        else:
            return False
    else:
        logging.warning(
            f"The regex will not be checked because the response's body might be unsafe to read in memory (too big or not text-based), for url: {response.url}"
        )
        return None
