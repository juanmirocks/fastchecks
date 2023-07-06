import datetime
from pydantic import BaseModel

from website_monitor.util import validate_regex, validate_url


# We use Pydantic classes for type safety and because they could be handy in the future for de/serialization.
# See benchmarks with other alternatives (e.g. NamedTuple): https://janhendrikewers.uk/pydantic_vs_protobuf_vs_namedtuple_vs_dataclasses.html
# Note that Pydantic V2 (released in 2023 June) promises a 5-50x speedup over V1: https://docs.pydantic.dev/2.0/blog/pydantic-v2-alpha/#headlines


class WebsiteCheck(BaseModel):
    url: str
    regex: str | None = None

    @classmethod
    def create_with_validation(cls, url: str, regex: str | None = None) -> "WebsiteCheck":
        """
        Validate the given URL and regex (if any), and return a WebsiteCheck instance.

        If the URL or regex are invalid, raise ValueError.
        """
        validate_url(url)
        if regex is not None:
            validate_regex(regex)
        return cls(url=url, regex=regex)

    @classmethod
    def create_without_validation(cls, url: str, regex: str | None = None) -> "WebsiteCheck":
        """
        Return a WebsiteCheck instance without validating the given URL and regex (if any).

        Only use this method if you are sure that the URL and regex are valid (e.g., they were validated before).
        """
        return cls(url=url, regex=regex)


class CheckResult(BaseModel):
    # The check that generated this result
    check: WebsiteCheck
    # Common values
    timestamp_start: datetime.datetime
    response_time: float
    # Connection error values
    timeout_error: bool
    host_error: bool
    other_error: bool
    # Response values (OK response, <400, or not)
    response_status: int | None
    regex_match: str | bool | None

    def __init__(self, **data) -> None:
        """
        Validate the input data.
        """
        super().__init__(**data)

        if self.check.regex is None:
            assert self.regex_match is None, "If there is no regex, regex_match MUST be None."
        else:
            assert isinstance(
                self.regex_match, (str, bool)
            ), "If there is a regex, regex_match MUST be either a string (match's text) or a boolean (match flag)."

    def is_success(self) -> bool:
        """
        Return True if the check was successful (i.e. no error, response is OK, and expected regex wax matched if any).
        """
        return self.is_partial_success() and (
            (self.check.regex is None) or ((self.regex_match is True) or isinstance(self.regex_match, str))
        )

    def is_partial_success(self) -> bool:
        """
        Return True if the check was partially successful (i.e. no error and response is OK).
        """
        return self.response_status is not None and self.response_status < 400

    @classmethod
    def response(
        cls,
        check: WebsiteCheck,
        timestamp_start: datetime.datetime,
        response_time: float,
        response_status: int,
        regex_match: str | bool | None,
    ) -> "CheckResult":
        """
        Return a successful CheckResult.
        """
        return cls(
            check=check,
            #
            timestamp_start=timestamp_start,
            response_time=response_time,
            #
            timeout_error=False,
            host_error=False,
            other_error=False,
            #
            response_status=response_status,
            regex_match=regex_match,
        )

    @classmethod
    def failure(
        cls,
        check: WebsiteCheck,
        timestamp_start: datetime.datetime,
        response_time: float,
        timeout_error: bool = False,
        host_error: bool = False,
        other_error: bool = False,
    ) -> "CheckResult":
        """
        Return a failed CheckResult.
        """
        assert (timeout_error or host_error or other_error) and not (
            timeout_error and host_error and other_error
        ), "There can only be one error type."

        return cls(
            check=check,
            #
            timestamp_start=timestamp_start,
            response_time=response_time,
            #
            timeout_error=timeout_error,
            host_error=host_error,
            other_error=other_error,
            #
            response_status=None,
            regex_match=None,
        )
