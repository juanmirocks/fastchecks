from abc import ABC, abstractmethod
from typing import NamedTuple


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


class CheckResultHandler(ABC):
    @abstractmethod
    def write(self, check_result: CheckResult) -> None:
        ...

    @abstractmethod
    def read_all(self) -> iter[CheckResult]:
        ...