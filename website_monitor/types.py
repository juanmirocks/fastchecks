from abc import ABC, abstractmethod
from typing import Iterator
from pydantic import BaseModel


# We use Pydantic for type safety
# See benchmarks with other alternatives (e.g. NamedTuple): https://janhendrikewers.uk/pydantic_vs_protobuf_vs_namedtuple_vs_dataclasses.html
# Note that Pydantic V2 (released in 2023 June) promises a 5-50x speedup over V1: https://docs.pydantic.dev/2.0/blog/pydantic-v2-alpha/#headlines
class CheckResult(BaseModel):
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

    async def __aenter__(self) -> "CheckResultHandler":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
