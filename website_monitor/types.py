import datetime
from pydantic import BaseModel

from website_monitor.util import validate_regex, validate_url


# We use Pydantic classes for type safety
# See benchmarks with other alternatives (e.g. NamedTuple): https://janhendrikewers.uk/pydantic_vs_protobuf_vs_namedtuple_vs_dataclasses.html
# Note that Pydantic V2 (released in 2023 June) promises a 5-50x speedup over V1: https://docs.pydantic.dev/2.0/blog/pydantic-v2-alpha/#headlines


class CheckResult(BaseModel):
    url: str
    timestamp_start: datetime.datetime
    response_time: float
    #
    response_status: int | None
    regex: str | None
    regex_match: str | bool | None
    """
    If there is no regex, this MUST be None.
    Else, if there is no match, this MUST be False.
    Else (if there is a match) this is either a string (the matched text) or True (if we don't care about the matched text).
    """
    timeout_error: bool = False


class WebsiteCheck(BaseModel):
    url: str
    regex: str | None = None

    @classmethod
    def create_with_validation(cls, url: str, regex: str | None = None) -> "WebsiteCheck":
        """
        Validate the given URL and regex (if any), and return a WebsiteCheck instance.

        If the URL is invalid, raise ValueError.
        If the regex is invalid, raise ValueError.
        """
        validate_url(url)
        if regex is not None:
            validate_regex(regex)
        return cls(url=url, regex=regex)


    @classmethod
    def create_without_validation(cls, url: str, regex: str | None = None) -> "WebsiteCheck":
        """
        Return a WebsiteCheck instance without validating the given URL and regex (if any).

        Note that this method is not recommended, because it is not safe.
        """
        return cls(url=url, regex=regex)
