from abc import ABC, abstractmethod
from typing import Iterator, NamedTuple


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
    async def write(self, check_result: CheckResult) -> None:
        ...

    @abstractmethod
    async def read_all(self) -> Iterator[CheckResult]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __del__(self) -> None:
        return await self.close()
