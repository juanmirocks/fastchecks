from abc import ABC, abstractmethod
from typing import Iterator

from website_monitor.types import CheckResult


class CheckResultSocket(ABC):
    @abstractmethod
    async def write(self, check_result: CheckResult) -> None:
        ...

    @abstractmethod
    async def read_all(self) -> Iterator[CheckResult]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self) -> "CheckResultSocket":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
