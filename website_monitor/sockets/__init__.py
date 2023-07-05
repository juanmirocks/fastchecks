from abc import ABC, abstractmethod
from typing import AsyncIterator

from website_monitor.types import CheckResult


class CheckResultSocket(ABC):
    @abstractmethod
    async def write(self, check_result: CheckResult) -> None:
        ...

    @abstractmethod
    async def read_all(self) -> AsyncIterator[CheckResult]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self) -> "CheckResultSocket":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


class WebsiteCheckSocket(ABC):
    @abstractmethod
    async def write(self, check: CheckResult) -> None:
        ...

    @abstractmethod
    async def read_all(self) -> AsyncIterator[AsyncIterator]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self) -> "WebsiteCheckSocket":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
