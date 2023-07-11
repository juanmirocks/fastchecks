from abc import ABC, abstractmethod
from typing import AsyncIterator
from pydantic.types import PositiveInt

from fastchecks.types import WebsiteCheckScheduled, CheckResult
from fastchecks.util import PRACTICAL_MAX_INT


# Sockets / Data Stores


class DataStoreSocket(ABC):
    # @abstractmethod
    async def is_datastore_ready(self) -> bool:
        """
        Return True if the socket's underlying data storage is ready to be used.
        Return False if it is not ready (e.g., it has not been initialized)
        """
        raise NotImplementedError

    # @abstractmethod
    async def init_datastore(self) -> bool:
        """
        Initialize the socket's underlying data storage.
        This method should be idempotent, i.e., it should not fail if the data storage is already initialized.
        Return True if the data storage was initialized anew or False if it was already initialized or could not initialize it.
        An Exception might be raised if the initialization fails.
        """
        raise NotImplementedError


class WebsiteCheckSocket(DataStoreSocket):
    @abstractmethod
    def is_closed(self) -> bool:
        ...

    @abstractmethod
    async def upsert(self, check: WebsiteCheckScheduled) -> int:
        """
        Upsert a check into the socket's underlying storage.
        That is, if the check's URL already exists, update the regex.
        Otherwise, insert/add/write the check.
        """
        ...

    @abstractmethod
    async def read_n(self, n: PositiveInt) -> AsyncIterator[WebsiteCheckScheduled]:
        ...

    async def read_all(self) -> AsyncIterator[WebsiteCheckScheduled]:
        """
        Read all checks from the socket's underlying storage.

        This is a sugar method that calls `read_n` with a practically infinite large number.
        Careful: Use this method only if the underlying storage can handle reading all checks (e.g., there not many written checks, which it's common).
        """
        return self.read_n(PRACTICAL_MAX_INT)

    @abstractmethod
    async def delete(self, url: str) -> int:
        """Return number of deleted checks, 0 (no actual deletion) or 1 (did delete)"""
        ...

    @abstractmethod
    async def delete_all(self, confirm: bool) -> int:
        """Return number of deleted checks. If the number is unknown, return a negative number like -1"""
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
    def is_closed(self) -> bool:
        ...

    @abstractmethod
    async def write(self, result: CheckResult) -> int:
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
