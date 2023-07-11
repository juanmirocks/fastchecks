import datetime
from pydantic import BaseModel

from fastchecks import util, vutil
from fastchecks import conf, require


# We use Pydantic classes for type safety and because they could be handy in the future for de/serialization.
# See benchmarks with other alternatives (e.g. NamedTuple): https://janhendrikewers.uk/pydantic_vs_protobuf_vs_namedtuple_vs_dataclasses.html
# Note that Pydantic V2 (released in 2023 June) promises a 5-50x speedup over V1: https://docs.pydantic.dev/2.0/blog/pydantic-v2-alpha/#headlines

_MAX_REPR_LEN: int = 410


class WebsiteCheck(BaseModel):
    url: str
    regex: str | None = None

    @classmethod
    def with_validation(cls, url: str, regex: str | None = None) -> "WebsiteCheck":
        """
        Validate the given URL and regex (if any), and return a WebsiteCheck instance.

        If the URL or regex are invalid, raise ValueError.
        """
        return cls(url=vutil.validated_web_url(url), regex=vutil.validated_regex_accepting_none(regex))

    @classmethod
    def without_validation(cls, url: str, regex: str | None = None) -> "WebsiteCheck":
        """
        Return a WebsiteCheck instance without validating the given URL and regex (if any).

        Only use this method if you are sure that the URL and regex are valid (e.g., they were validated before).
        """
        return cls(url=url, regex=regex)

    def __repr__(self) -> str:
        return util.shorten_str(super().__repr__(), max=_MAX_REPR_LEN)

    def __str__(self) -> str:
        return util.shorten_str(super().__repr__(), max=_MAX_REPR_LEN)


class WebsiteCheckScheduled(WebsiteCheck):
    """
    WebsiteCheck with an schedule.
    """

    # url: str
    # regex: str | None = None
    interval_seconds: int | None
    """If None, later a system's default value will be used."""

    @classmethod
    def with_check(cls, check: WebsiteCheck, interval_seconds: int | None) -> "WebsiteCheckScheduled":
        return cls(
            url=check.url, regex=check.regex, interval_seconds=conf.validated_interval_accepting_none(interval_seconds)
        )


class CheckResult(BaseModel):
    #
    check: WebsiteCheck
    """The check that generated this result"""
    #
    # Common values
    #
    timestamp_start: datetime.datetime
    response_time: float
    #
    # Connection error values
    #
    timeout_error: bool
    host_error: bool
    other_error: bool
    #
    # Response values (note: OK response, <400, or not)
    #
    response_status: int | None
    regex_match: str | bool | None
    """
    str: the tested regex matched and the matched string is this value.
    bool True: the tested regex matched but the matched string is not available.
    bool False: the tested regex did not match.
    None: means "not tested" (e.g. there was no regex to test, the response was not OK, or the response body was ignored because it was too big or not text).
    """

    def __init__(self, **data) -> None:
        """
        Validate the input data.
        """
        super().__init__(**data)

        if self.check.regex is None:
            require(self.regex_match is None, "If there is no regex, regex_match MUST be None.")

    def __repr__(self) -> str:
        return util.shorten_str(super().__repr__(), max=_MAX_REPR_LEN)

    def __str__(self) -> str:
        return util.shorten_str(super().__repr__(), max=_MAX_REPR_LEN)

    def is_success(self) -> bool:
        """
        Return True if the check was successful (i.e. no error, response is OK, and expected regex wax matched if any).
        """
        return self.is_response_ok() and self.is_regex_validated()

    def is_response_ok(self) -> bool:
        """
        Return True if the check was partially successful (i.e. no error and response is OK).
        """
        return self.response_status is not None and self.response_status < 400

    def is_regex_validated(self) -> bool:
        """
        Return True if the regex was validated (i.e. there was a regex and it matched).
        """
        return self.check.regex is None or self.is_regex_match_truthy()

    def is_regex_match_truthy(self) -> bool:
        """
        Return True if the regex matched and it's either True or the matched string is present.

        Note: we consider a regex match to be truthy even if the matched string is the empty string.
        This could be changed.
        """
        return self.regex_match is True or isinstance(self.regex_match, str)

    def regex_match_to_bool_or_none(self) -> bool | None:
        return None if self.regex_match is None else self.is_regex_match_truthy()

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
        require(
            (timeout_error or host_error or other_error) and not (timeout_error and host_error and other_error),
            "There can only be one error type.",
        )

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
