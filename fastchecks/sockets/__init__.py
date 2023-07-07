from abc import ABC, abstractmethod
from typing import AsyncIterator
from pydantic.types import PositiveInt

from fastchecks.types import WebsiteCheck, CheckResult


class WebsiteCheckSocket(ABC):
    @abstractmethod
    async def upsert(self, check: WebsiteCheck) -> None:
        """
        Upsert a check into the socket's underlying storage.
        That is, if the check's URL already exists, update the regex.
        Otherwise, insert/add/write the check.
        """
        ...

    @abstractmethod
    async def read_last_n(self, n: PositiveInt) -> AsyncIterator[CheckResult]:
        ...

    @abstractmethod
    async def delete(self, url: str) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self) -> "WebsiteCheckSocket":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


class CheckResultSocket(ABC):
    @abstractmethod
    async def write(self, result: CheckResult) -> None:
        ...

    @abstractmethod
    async def read_last_n(self, n: PositiveInt) -> AsyncIterator[CheckResult]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self) -> "CheckResultSocket":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
